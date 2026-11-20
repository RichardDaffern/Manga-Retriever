"""Restore *existing* GitHub Actions manga artifacts privately to Windows.

Does not initiate website scraping, copy to a public Actions artifact, or
write to Hugging Face. The historical artifacts already exist and expire
after seven days. Uses pinned artifact IDs, validates complete ZIP+CBZ media,
and never overwrites a previously downloaded folder.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from manga_retriever.relife import ReLIFEError, _inspect_cbz

REPOSITORY = "RichardDaffern/Manga-Retriever"
MANIFEST = Path(__file__).with_name("historical_manga_artifacts_20261120.json")
MAX_OUTER_MEMBERS = 5000
MAX_OUTER_BYTES = 3_000_000_000
MAX_OUTER_UNCOMPRESSED = 5_000_000_000
MAX_ARCHIVES_PER_ARTIFACT = 1500
MAX_WORKERS = 3
VALID_NAME = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,130}\Z")


class RecoveryError(ValueError):
    """Cannot safely retrieve or validate this pre-existing artifact."""


def _safe_folder(folder: Path) -> None:
    if folder.is_symlink() or (folder.exists() and not folder.is_dir()):
        raise RecoveryError("Output must be an ordinary directory")
    if any(parent.is_symlink() for parent in folder.parents):
        raise RecoveryError("Output cannot be below a symlink")


def load_manifest(path: Path = MANIFEST) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if (manifest.get("schemaVersion") != 1
            or manifest.get("sourceRepository") != REPOSITORY
            or not isinstance(manifest.get("titles"), dict)):
        raise RecoveryError("Unknown or untrusted historical artifact manifest")
    seen_ids: set[int] = set()
    for slug, series in manifest["titles"].items():
        if not VALID_NAME.fullmatch(slug):
            raise RecoveryError("Invalid slug in historical artifact manifest")
        items = series.get("items")
        if not isinstance(items, list) or not items:
            raise RecoveryError("Empty artifact set")
        for item in items:
            if (type(item.get("artifactId")) is not int or item["artifactId"] <= 0
                    or type(item.get("runId")) is not int or item["runId"] <= 0
                    or not isinstance(item.get("name"), str)
                    or not VALID_NAME.fullmatch(item["name"])
                    or not isinstance(item.get("range"), str)
                    or not VALID_NAME.fullmatch(item["range"])
                    or item["artifactId"] in seen_ids):
                raise RecoveryError("Unsafe, duplicated or invalid artifact record")
            seen_ids.add(item["artifactId"])
    return manifest


def _gh_json(endpoint: str, *, runner=subprocess.run) -> dict:
    result = runner(["gh", "api", endpoint], capture_output=True, text=True,
                    check=False, timeout=60)
    if result.returncode != 0:
        raise RecoveryError("GitHub CLI could not read the artifact; authenticate with 'gh auth login'")
    try:
        document = json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RecoveryError("Invalid GitHub API response") from exc
    if not isinstance(document, dict):
        raise RecoveryError("Unrecognised GitHub artifact metadata")
    return document


def _download_archive(item: dict, destination_zip: Path, *, runner=subprocess.run) -> None:
    endpoint = f"repos/{REPOSITORY}/actions/artifacts/{item['artifactId']}/zip"
    with destination_zip.open("xb") as output:
        response = runner(["gh", "api", endpoint], stdout=output,
                          stderr=subprocess.PIPE, check=False, timeout=1200)
    if response.returncode != 0 or not zipfile.is_zipfile(destination_zip):
        raise RecoveryError("GitHub artifact ZIP unavailable or invalid; no output published")
    if not 100 <= destination_zip.stat().st_size <= MAX_OUTER_BYTES:
        raise RecoveryError("Downloaded artifact ZIP exceeds size quota or is empty")


def _safe_extract(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        if not 1 <= len(infos) <= MAX_OUTER_MEMBERS:
            raise RecoveryError("Unexpected artifact ZIP member count")
        total = 0
        paths: set[str] = set()
        for entry in infos:
            name = entry.filename
            if not name or "\\" in name or "\0" in name or name.startswith("/"):
                raise RecoveryError("Unsafe archive member name")
            p = PurePosixPath(name)
            if p.is_absolute() or not p.parts or any(x in ("..", ".", "") for x in p.parts):
                raise RecoveryError("Archive path traversal")
            if len(p.parts) > 12 or len(name) > 400:
                raise RecoveryError("Excessive artifact path")
            normalised = p.as_posix().casefold()
            if normalised in paths:
                raise RecoveryError("Duplicate artifact member path")
            paths.add(normalised)
            kind = stat.S_IFMT(entry.external_attr >> 16)
            if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise RecoveryError("Special or symlink artifact member")
            if entry.flag_bits & 1 or entry.file_size < 0:
                raise RecoveryError("Encrypted or invalid ZIP file")
            if entry.file_size > max(1, entry.compress_size) * 100:
                raise RecoveryError("Suspicious artifact compression ratio")
            total += entry.file_size
            if total > MAX_OUTER_UNCOMPRESSED:
                raise RecoveryError("Unpacked media exceeds safety budget")
        for entry in infos:
            path = destination.joinpath(*PurePosixPath(entry.filename).parts)
            if entry.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as src, path.open("xb") as dest:
                    shutil.copyfileobj(src, dest, length=1024 * 1024)


def _audit_files(directory: Path) -> dict:
    if directory.is_symlink() or not directory.is_dir():
        raise RecoveryError("Missing recovery directory")
    if any(p.is_symlink() for p in directory.rglob("*")):
        raise RecoveryError("Symlink in recovered files")
    archives = sorted(p for p in directory.rglob("*.cbz") if p.is_file())
    if not 1 <= len(archives) <= MAX_ARCHIVES_PER_ARTIFACT:
        raise RecoveryError("Missing CBZ chapter files or excessive archive count")
    results = []
    try:
        for path in archives:
            report = _inspect_cbz(path)
            results.append({
                "file": path.relative_to(directory).as_posix(),
                "sha256": report["sha256"],
                "pages": report["verifiedPageCount"],
                "size": path.stat().st_size,
            })
    except (ReLIFEError, OSError, zipfile.BadZipFile) as exc:
        raise RecoveryError("Recovered CBZ contained unsafe or invalid image bytes") from exc
    pages = sum(x["pages"] for x in results)
    if pages <= 0:
        raise RecoveryError("Recovered archives have no actual verified images")
    audits = [p for p in directory.rglob("quality_audit.json") if p.is_file()]
    audits += [p for p in directory.rglob("relife_quality_audit.json") if p.is_file()]
    if len(audits) > 1:
        raise RecoveryError("More than one source quality report in a single artifact")
    if audits:
        raw = audits[0].read_bytes()
        if len(raw) > 5_000_000:
            raise RecoveryError("Oversized source audit")
        source_audit = json.loads(raw)
        if (type(source_audit.get("verifiedArchives")) is int
                and source_audit["verifiedArchives"] != len(results)):
            raise RecoveryError("Source audit archive count mismatch")
        if (type(source_audit.get("verifiedPages")) is int
                and source_audit["verifiedPages"] != pages):
            raise RecoveryError("Source audit image count mismatch")
    return {"verifiedCBZ": len(results), "verifiedPages": pages, "archives": results}


def _verify_existing(directory: Path, item: dict) -> dict:
    _safe_folder(directory)
    if not directory.is_dir():
        raise RecoveryError("A prior recovery folder has disappeared")
    report_path = directory / "recovery-verification.json"
    if report_path.is_symlink() or not report_path.is_file():
        raise RecoveryError("Existing destination lacks trustworthy recovery metadata")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("artifactId") != item["artifactId"]:
        raise RecoveryError("Existing artifact ID differs; refusing to overwrite")
    actual = _audit_files(directory)
    expected = {x["file"]: x for x in report.get("archives", [])}
    if (len(actual["archives"]) != len(expected)
            or actual["verifiedPages"] != report.get("verifiedPages")
            or any(expected.get(x["file"], {}).get("sha256") != x["sha256"]
                   for x in actual["archives"])):
        raise RecoveryError("Existing recovered pages differ from original verification")
    report["outcome"] = "already-verified"
    return report


def recover_one(slug: str, item: dict, root: Path, *, runner=subprocess.run) -> dict:
    folder = root / slug / item["name"]
    _safe_folder(folder)
    if folder.exists():
        return _verify_existing(folder, item)
    folder.parent.mkdir(parents=True, exist_ok=True)
    endpoint = f"repos/{REPOSITORY}/actions/artifacts/{item['artifactId']}"
    remote = _gh_json(endpoint, runner=runner)
    remote_run = remote.get("workflow_run") or {}
    if (remote.get("id") != item["artifactId"] or remote.get("name") != item["name"]
            or remote_run.get("id") != item["runId"] or remote.get("expired") is not False):
        raise RecoveryError("GitHub artifact identity mismatch or expired artifact")
    with tempfile.TemporaryDirectory(prefix=".manga-recovery-", dir=folder.parent) as tmp:
        stage = Path(tmp)
        archive_zip = stage / "downloaded-artifact.zip"
        _download_archive(item, archive_zip, runner=runner)
        remote_size = remote.get("size_in_bytes")
        if type(remote_size) is int and remote_size != archive_zip.stat().st_size:
            raise RecoveryError("GitHub artifact ZIP length differs from source metadata")
        files = stage / "content"
        files.mkdir()
        _safe_extract(archive_zip, files)
        report = {
            "artifactId": item["artifactId"],
            "artifactName": item["name"],
            "runId": item["runId"],
            "sourceRepository": REPOSITORY,
            "sourceRunUrl": f"https://github.com/{REPOSITORY}/actions/runs/{item['runId']}",
            "sourceArchiveSize": archive_zip.stat().st_size,
            "recordedExpiry": remote.get("expires_at"),
            "fetchedAtUtc": datetime.now(UTC).isoformat(),
            "originalBytesPreserved": True,
            "outputRemainsOnOwnersComputer": True,
            "publicMediaReuploaded": False,
            "completeSeriesIndependentlyProven": False,
            **_audit_files(files),
            "outcome": "downloaded-and-verified",
        }
        (files / "recovery-verification.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if folder.exists() or folder.is_symlink():
            raise RecoveryError("Destination appeared while fetching artifact")
        os.replace(files, folder)
        return report


def recover_all(slugs: list[str], root: Path, *, workers: int = 3,
                runner=subprocess.run, manifest: dict | None = None) -> dict:
    document = manifest or load_manifest()
    if (not slugs or len(slugs) != len(set(slugs))
            or any(slug not in document["titles"] for slug in slugs)):
        raise RecoveryError("Unknown or duplicate manga title selection")
    if type(workers) is not int or not 1 <= workers <= MAX_WORKERS:
        raise RecoveryError("Choose 1, 2 or 3 concurrent downloads")
    _safe_folder(root)
    root.mkdir(parents=True, exist_ok=True)
    chosen = [(slug, item) for slug in slugs for item in document["titles"][slug]["items"]]
    outcomes: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(workers, len(chosen))) as executor:
        tasks = {executor.submit(recover_one, slug, item, root, runner=runner):
                 (slug, item) for slug, item in chosen}
        for task in as_completed(tasks):
            slug, item = tasks[task]
            try:
                data = task.result()
                outcomes.append({"slug": slug, "range": item["range"], **data})
                print(f"VERIFIED {slug}/{item['range']}: {data['verifiedCBZ']} CBZ "
                      f"and {data['verifiedPages']} image pages", flush=True)
            except (RecoveryError, OSError, ValueError, subprocess.SubprocessError) as exc:
                outcomes.append({"slug": slug, "range": item["range"], "artifactId": item["artifactId"],
                                 "outcome": "failed", "error": str(exc)[:240]})
                print(f"FAILED {slug}/{item['range']}: {exc}", file=sys.stderr, flush=True)
    outcomes.sort(key=lambda x: (x["slug"], x["range"]))
    result = {
        "schemaVersion": 1,
        "status": "all-artifacts-verified" if all(x["outcome"] != "failed" for x in outcomes)
                  else "partial",
        "processed": len(outcomes),
        "verifiedArtifacts": sum(x["outcome"] != "failed" for x in outcomes),
        "verifiedImages": sum(x.get("verifiedPages", 0) for x in outcomes),
        "downloadedTo": str(root.resolve()),
        "completeSeriesIndependentlyProven": False,
        "results": outcomes,
    }
    fd, name = tempfile.mkstemp(prefix=".recovery-", suffix=".json", dir=root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
            output.write("\n")
        os.replace(name, root / "historical-recovery-status.json")
    finally:
        Path(name).unlink(missing_ok=True)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Privately recover existing, expiring manga Actions CBZ artifacts")
    parser.add_argument("--titles", default="all", help="Comma-separated slugs or 'all'")
    parser.add_argument("--output-root", type=Path, required=True,
                        help="Private output folder outside this public checkout")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest()
        titles = list(manifest["titles"]) if args.titles == "all" else args.titles.split(",")
        if shutil.which("gh") is None:
            raise RecoveryError("GitHub CLI 'gh' not found; install gh and run 'gh auth login'")
        results = recover_all(titles, args.output_root, workers=args.workers,
                              manifest=manifest)
    except (OSError, RecoveryError, ValueError) as exc:
        print(f"Artifact recovery cannot start: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({key: results[key] for key in
                      ("status", "processed", "verifiedArtifacts", "verifiedImages", "downloadedTo")}))
    return 0 if results["status"] == "all-artifacts-verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
