"""Windows-compatible, verification-first retrieval of approved GitHub artefacts.

The GitHub CLI performs authenticated transport. This module validates the
independent metadata receipt, downloaded export, archive hash and provenance.
It never accepts an arbitrary repository, URL, external executable or URL key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .batch import APPROVED, GITHUB_REPO, BatchError, _load_registry, _parse_date, validate_receipt

MAX_EXPORT_BYTES = 5_000_000_000
MAX_BUNDLE_FILES = 50_000
CHUNK = 1024 * 1024


class RetrievalError(ValueError):
    """Unsafe registry, expired artefact, corrupted export or failed retrieval."""


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _check_export(folder: Path, receipt: dict[str, Any], verifier: Callable[[Path], dict] | None = None) -> None:
    if not folder.is_dir() or folder.is_symlink():
        raise RetrievalError("Missing or symlinked downloaded export")
    if verifier is None:
        from .importer import verify_export
        verifier = verify_export
    if verifier(folder) != {"series": 1, "chapters": receipt["chapters"], "pages": receipt["pages"]}:
        raise RetrievalError("Export does not match approved page/chapter counts")
    manifest = json.loads((folder / "download_manifest.json").read_text(encoding="utf-8"))
    licensed = manifest.get("licensedSource") if isinstance(manifest, dict) else None
    if (not isinstance(licensed, dict) or licensed.get("provider") != receipt["provider"]
            or licensed.get("episode") != receipt["episode"]
            or licensed.get("licence") != receipt["licence"]):
        raise RetrievalError("Downloaded artefact source provenance disagrees with receipt")
    chapter_files = list((folder / "chapters").glob("*.cbz"))
    if len(chapter_files) != 1 or chapter_files[0].is_symlink() or _sha(chapter_files[0]) != receipt["sha256"]:
        raise RetrievalError("Downloaded CBZ checksum mismatch")


def choose_receipts(registry: Path, *, key: str | None = None, run_id: int | None = None,
                    now: datetime | None = None) -> list[dict[str, Any]]:
    """Select the newest unexpired authorised artefact per source key."""
    if key is not None and key not in APPROVED:
        raise RetrievalError("Unsupported source key")
    if run_id is not None and (type(run_id) is not int or run_id <= 0):
        raise RetrievalError("Invalid GitHub run ID")
    try:
        records = _load_registry(registry)["downloads"]
    except BatchError as exc:
        raise RetrievalError(str(exc)) from exc
    now = (now or datetime.now(UTC)).astimezone(UTC)
    chosen: dict[str, dict[str, Any]] = {}
    for value in records:
        rec = validate_receipt(value)
        if (key is not None and rec["key"] != key) or (run_id is not None and rec["runId"] != run_id):
            continue
        if _parse_date(rec["expiresAt"]) <= now:
            continue
        earlier = chosen.get(rec["key"])
        if earlier is None or (rec["completedAt"], rec["runId"], rec["artifactId"]) > (
            earlier["completedAt"], earlier["runId"], earlier["artifactId"]
        ):
            chosen[rec["key"]] = rec
    if not chosen:
        raise RetrievalError("No matching unexpired approved artefacts in registry")
    return [chosen[k] for k in sorted(chosen)]


def retrieve_one(receipt: dict[str, Any], destination: Path, *, runner=subprocess.run,
                 verifier: Callable[[Path], dict] | None = None, skip_existing: bool = True) -> str:
    """Download one exact named Actions artefact, verify, and atomically publish."""
    try:
        rec = validate_receipt(receipt)
    except BatchError as exc:
        raise RetrievalError(str(exc)) from exc
    if _parse_date(rec["expiresAt"]) <= datetime.now(UTC):
        raise RetrievalError("Artefact expired; rerun the authorised Actions download")
    dest = Path(destination)
    if dest.exists() or dest.is_symlink():
        if not skip_existing:
            raise RetrievalError("Destination exists; refusing overwrite")
        _check_export(dest, rec, verifier=verifier)
        return "skipped-verified"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.parent.is_symlink():
        raise RetrievalError("Symlinked destination parent is not permitted")
    artifact_name = f"licensed-manga-{rec['runId']}-{rec['key'].replace(':', '-')}"
    work = Path(tempfile.mkdtemp(prefix=".manga-gh-retrieve-", dir=dest.parent))
    try:
        try:
            runner(
                ["gh", "run", "download", str(rec["runId"]), "--repo", GITHUB_REPO,
                 "--name", artifact_name, "--dir", str(work)],
                check=True, timeout=600,
            )
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise RetrievalError("GitHub CLI download failed; check `gh auth status`, run and retention") from exc
        _check_export(work, rec, verifier=verifier)
        if dest.exists() or dest.is_symlink():
            raise RetrievalError("Destination appeared during retrieval; refusing overwrite")
        work.rename(dest)
        return "downloaded-verified"
    finally:
        if work.exists():
            shutil.rmtree(work)


def retrieve_registered(registry: Path, directory: Path, *, key: str | None = None,
                        run_id: int | None = None, skip_existing: bool = True,
                        runner=subprocess.run, verifier=None) -> dict[str, str]:
    """Fetch one or all newest licensed exports without overwriting valid files."""
    chosen = choose_receipts(registry, key=key, run_id=run_id)
    results = {}
    for rec in chosen:
        slug = rec["key"].replace(":", "-")
        results[rec["key"]] = retrieve_one(
            rec, Path(directory) / f"{slug}-run-{rec['runId']}", runner=runner,
            verifier=verifier, skip_existing=skip_existing,
        )
    return results


def bundle_verified(exports: Path, output: Path, *, verifier=None) -> dict[str, int]:
    """Combine individually verified exports into one portable, checked ZIP.

    This is an offline owner action, not a GitHub Actions artefact. No resizing,
    conversions or modification of source bytes occurs inside the ZIP.
    """
    source, output = Path(exports), Path(output)
    if not source.is_dir() or source.is_symlink() or output.exists() or output.is_symlink():
        raise RetrievalError("Source must be a real folder and output must be new")
    if output.resolve().is_relative_to(source.resolve()):
        raise RetrievalError("Bundle destination cannot be inside source")
    children = sorted(source.iterdir(), key=lambda x: x.name.casefold())
    if not children or len(children) > 20 or any(not p.is_dir() or p.is_symlink() for p in children):
        raise RetrievalError("Expected 1 to 20 separate verified export directories")
    if verifier is None:
        from .importer import verify_export
        verifier = verify_export
    files: list[tuple[Path, str]] = []
    total = 0
    for folder in children:
        verifier(folder)
        if not all(c.isalnum() or c in "-_." for c in folder.name) or folder.name in {".", ".."}:
            raise RetrievalError("Unsafe output folder name")
        for path in sorted(folder.rglob("*")):
            if path.is_symlink():
                raise RetrievalError("Symlinks forbidden in export bundle")
            if path.is_dir():
                continue
            if not path.is_file():
                raise RetrievalError("Unsupported special file in export")
            relative = path.relative_to(source).as_posix()
            total += path.stat().st_size
            files.append((path, relative))
            if len(files) > MAX_BUNDLE_FILES or total > MAX_EXPORT_BYTES:
                raise RetrievalError("Bundle exceeds file or byte quota")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, filename = tempfile.mkstemp(prefix=".manga-bundle-", suffix=".zip", dir=output.parent)
    os.close(fd)
    temp = Path(filename)
    try:
        hashes = {}
        with zipfile.ZipFile(temp, "w", allowZip64=True, compression=zipfile.ZIP_STORED) as archive:
            for path, relative in files:
                digest = _sha(path)
                archive.write(path, relative)
                if _sha(path) != digest:
                    raise RetrievalError("Source modified during bundling")
                hashes[relative] = digest
            summary = {"schemaVersion": 1, "exports": [x.name for x in children], "files": hashes}
            archive.writestr("manga_bundle_manifest.json", json.dumps(summary, indent=2, sort_keys=True) + "\n")
        with zipfile.ZipFile(temp, "r") as check:
            if set(check.namelist()) != set(hashes) | {"manga_bundle_manifest.json"}:
                raise RetrievalError("Bundle member inventory mismatch")
            for relative, expected in hashes.items():
                digest = hashlib.sha256()
                with check.open(relative) as stream:
                    for part in iter(lambda: stream.read(CHUNK), b""):
                        digest.update(part)
                if digest.hexdigest() != expected:
                    raise RetrievalError("Bundled file failed SHA-256 verification")
        if output.exists() or output.is_symlink():
            raise RetrievalError("Destination appeared during bundling")
        temp.rename(output)
        return {"exports": len(children), "files": len(files), "bytes": total}
    finally:
        temp.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download and verify allowlisted manga artefacts (GitHub CLI required)")
    commands = parser.add_subparsers(dest="command", required=True)
    pull = commands.add_parser("download", help="Fetch newest unexpired, approved GitHub Actions exports")
    pull.add_argument("--registry", type=Path, default=Path("downloaded_manga.json"))
    pull.add_argument("--directory", type=Path, required=True)
    pull.add_argument("--key", choices=sorted(APPROVED))
    pull.add_argument("--run-id", type=int)
    pull.add_argument("--no-skip-existing", action="store_true")
    bundle = commands.add_parser("bundle", help="Bundle all separately verified exports into one local ZIP")
    bundle.add_argument("--exports", type=Path, required=True)
    bundle.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "download":
            result = retrieve_registered(args.registry, args.directory, key=args.key,
                                         run_id=args.run_id, skip_existing=not args.no_skip_existing)
        else:
            result = bundle_verified(args.exports, args.output)
        print(json.dumps({"status": "verified", **result}, sort_keys=True))
        return 0
    except (RetrievalError, BatchError, OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"Retrieval failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
