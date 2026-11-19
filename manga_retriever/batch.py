"""Allowlisted batch dispatch, short-lived artefact receipts and metadata registry.

No arbitrary source URLs. Media never enters the public Git repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

APPROVED = {"peppercarrot:26": {"provider": "peppercarrot", "episode": 26, "pages": 6}}
GITHUB_REPO = "RichardDaffern/Manga-Retriever"
ARTIFACT_RE = re.compile(r"https://github\.com/RichardDaffern/Manga-Retriever/actions/runs/([1-9][0-9]*)/artifacts/([1-9][0-9]*)")
HASH_RE = re.compile(r"[a-f0-9]{64}")
RECORD_KEYS = {
    "schemaVersion", "key", "provider", "episode", "title", "licence", "runId",
    "artifactId", "artifactUrl", "completedAt", "expiresAt", "chapters", "pages", "sha256",
}


class BatchError(ValueError):
    """Invalid approved selection, receipt or registry state."""


def parse_selection(text: str) -> list[str]:
    if not isinstance(text, str) or len(text) > 512:
        raise BatchError("Batch selection is too large")
    items = [item.strip() for item in re.split(r"[,\n]", text) if item.strip()]
    if not 1 <= len(items) <= 20 or len(set(items)) != len(items):
        raise BatchError("Select 1 to 20 distinct approved manga identifiers")
    if any(item not in APPROVED for item in items):
        raise BatchError("Unknown or unapproved source; no arbitrary URLs accepted")
    return items


def parse_matrix(value: str) -> list[str]:
    try:
        data = json.loads(value)
    except ValueError as exc:
        raise BatchError("Invalid batch matrix") from exc
    if not isinstance(data, list) or not data or len(data) > 20:
        raise BatchError("Invalid batch matrix")
    keys = []
    for item in data:
        if (
            not isinstance(item, dict)
            or set(item) != {"key", "slug"}
            or not isinstance(item["key"], str)
            or item["slug"] != item["key"].replace(":", "-")
        ):
            raise BatchError("Invalid approved batch job")
        keys.append(item["key"])
    return parse_selection(",".join(keys))


def _parse_date(value: object) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value):
        raise BatchError("Invalid UTC registry timestamp")
    try:
        d = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise BatchError("Invalid UTC date") from exc
    return d


def _format_date(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_receipt(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != RECORD_KEYS or value.get("schemaVersion") != 1:
        raise BatchError("Unknown or incomplete receipt schema")
    key = value.get("key")
    if not isinstance(key, str) or key not in APPROVED:
        raise BatchError("Receipt source not explicitly authorised")
    details = APPROVED[key]
    if (value.get("provider"), value.get("episode")) != (details["provider"], details["episode"]):
        raise BatchError("Source identity mismatch")
    if value.get("licence") != "CC BY 4.0" or value.get("title") != "Pepper&Carrot Episode 26: Books Are Great":
        raise BatchError("Unrecognised rights/title metadata")
    if type(value.get("runId")) is not int or type(value.get("artifactId")) is not int:
        raise BatchError("Non-integer GitHub artefact identifier")
    url = value.get("artifactUrl")
    match = ARTIFACT_RE.fullmatch(url) if isinstance(url, str) else None
    if not match or (int(match[1]), int(match[2])) != (value["runId"], value["artifactId"]):
        raise BatchError("Receipt artefact URL does not match expected GitHub run")
    if type(value.get("chapters")) is not int or value["chapters"] != 1:
        raise BatchError("Wrong chapter count")
    if type(value.get("pages")) is not int or value["pages"] != details["pages"]:
        raise BatchError("Wrong licensed page count")
    if not isinstance(value.get("sha256"), str) or not HASH_RE.fullmatch(value["sha256"]):
        raise BatchError("Invalid archive hash")
    start, end = _parse_date(value.get("completedAt")), _parse_date(value.get("expiresAt"))
    if not timedelta(0) < end - start <= timedelta(days=90):
        raise BatchError("Invalid artefact retention window")
    return dict(value)


def _load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schemaVersion": 1, "downloads": []}
    if path.is_symlink():
        raise BatchError("Registry may not be a symlink")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BatchError("Invalid registry JSON") from exc
    if (not isinstance(data, dict) or set(data) != {"schemaVersion", "downloads"}
            or data["schemaVersion"] != 1 or not isinstance(data["downloads"], list)
            or len(data["downloads"]) > 10000):
        raise BatchError("Unsupported registry document")
    for record in data["downloads"]:
        validate_receipt(record)
    keys = [(x["runId"], x["artifactId"]) for x in data["downloads"]]
    if len(keys) != len(set(keys)):
        raise BatchError("Duplicated artefact identities in registry")
    return data


def _atomic_text(path: Path, value: str) -> None:
    if path.is_symlink():
        raise BatchError("Refusing to write through registry symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".manga-registry-", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _markdown(registry: dict[str, Any]) -> str:
    lines = [
        "# Downloaded manga", "", "Metadata-only history of *verified, licensed* downloads.",
        "Actual CBZs and original images are short-lived GitHub Actions artefacts, never Git files.",
        "Artefacts may be manually deleted before their recorded expiry; check GitHub before relying on a link.",
        "", "| Manga | Chapters | Pages | Run / artefact | Expiry (UTC) |", "| --- | ---: | ---: | --- | --- |",
    ]
    for rec in registry["downloads"]:
        lines.append(
            f'| {rec["title"]} | {rec["chapters"]} | {rec["pages"]} | '
            f'[Run {rec["runId"]}]({rec["artifactUrl"]}) | {rec["expiresAt"]} |'
        )
    if not registry["downloads"]:
        lines.append("| No verified downloads yet | | | | |")
    return "\n".join(lines) + "\n"


def consolidate(receipt_dir: Path, expected: list[str], registry_path: Path, markdown_path: Path, status_path: Path) -> dict[str, Any]:
    """Index completed jobs even when another job failed; publish missing plan."""
    if len(set(expected)) != len(expected) or not expected or any(x not in APPROVED for x in expected):
        raise BatchError("Unknown expected job set")
    if receipt_dir.is_symlink() or not receipt_dir.is_dir():
        raise BatchError("Receipt directory missing or symlinked")
    files = sorted(receipt_dir.rglob("*.json"))
    if len(files) > 20 or any(p.is_symlink() for p in files):
        raise BatchError("Too many or symlinked receipts")
    new: dict[str, dict[str, Any]] = {}
    for path in files:
        if path.stat().st_size > 10000:
            raise BatchError("Oversized receipt")
        try:
            rec = validate_receipt(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as exc:
            raise BatchError("Malformed receipt") from exc
        if rec["key"] not in expected or rec["key"] in new:
            raise BatchError("Unexpected or duplicate batch receipt")
        new[rec["key"]] = rec
    registry = _load_registry(registry_path)
    known = {(r["runId"], r["artifactId"]) for r in registry["downloads"]}
    for rec in new.values():
        if (rec["runId"], rec["artifactId"]) not in known:
            registry["downloads"].append(rec)
    registry["downloads"].sort(key=lambda r: (r["completedAt"], r["key"], r["artifactId"]))
    if len(registry["downloads"]) > 10000:
        raise BatchError("Registry retention budget exceeded")
    missing = [item for item in expected if item not in new]
    status = {"schemaVersion": 1, "completed": sorted(new), "missing": missing}
    _atomic_text(registry_path, json.dumps(registry, indent=2, sort_keys=True) + "\n")
    _atomic_text(markdown_path, _markdown(registry))
    _atomic_text(status_path, json.dumps(status, indent=2, sort_keys=True) + "\n")
    return status


def receipt_from_export(
    key: str, export: Path, run_id: int, artifact_id: int, artifact_url: str,
    *, now: datetime | None = None, retention_days: int = 7,
    verifier=None,
) -> dict[str, Any]:
    """Require byte-level export verification before indexing any GitHub artefact."""
    if key not in APPROVED or not 1 <= retention_days <= 90:
        raise BatchError("Unsupported source/retention")
    if type(run_id) is not int or run_id < 1 or type(artifact_id) is not int or artifact_id < 1:
        raise BatchError("Invalid upload identifiers")
    if verifier is None:
        from .importer import verify_export
        verifier = verify_export
    counts = verifier(export)
    if counts != {"series": 1, "chapters": 1, "pages": 6}:
        raise BatchError("Verified export is not the six-page licensed episode")
    manifest = json.loads((export / "download_manifest.json").read_text(encoding="utf-8"))
    licensed = manifest.get("licensedSource") if isinstance(manifest, dict) else None
    if (
        not isinstance(licensed, dict)
        or licensed.get("provider") != "peppercarrot"
        or licensed.get("episode") != 26
        or licensed.get("licence") != "CC BY 4.0"
    ):
        raise BatchError("Licensed source provenance missing")
    pages = licensed.get("pages")
    if not isinstance(pages, list) or len(pages) != 6 or [x.get("pageNumber") for x in pages if isinstance(x, dict)] != list(range(1, 7)):
        raise BatchError("Licensed source page plan incomplete")
    from .peppercarrot import _official_page_url, LICENCE_URL, SOURCE_PAGE
    if licensed.get("sourcePage") != SOURCE_PAGE or licensed.get("licenceUrl") != LICENCE_URL:
        raise BatchError("Unapproved source page/licence")
    for page in pages:
        checked = _official_page_url(page.get("sourceUrl", ""))
        if checked is None or checked[0] != page["pageNumber"] or not HASH_RE.fullmatch(page.get("sha256", "")):
            raise BatchError("Unverified page URL or hash in source provenance")
    cbz_files = sorted((export / "chapters").glob("*.cbz"))
    if len(cbz_files) != 1 or cbz_files[0].is_symlink():
        raise BatchError("Exactly one verified chapter CBZ expected")
    sha = hashlib.sha256()
    with cbz_files[0].open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    current = (now or datetime.now(UTC)).astimezone(UTC)
    receipt = {
        "schemaVersion": 1, "key": key, "provider": "peppercarrot", "episode": 26,
        "title": "Pepper&Carrot Episode 26: Books Are Great", "licence": "CC BY 4.0",
        "runId": run_id, "artifactId": artifact_id, "artifactUrl": artifact_url,
        "completedAt": _format_date(current), "expiresAt": _format_date(current + timedelta(days=retention_days)),
        "chapters": 1, "pages": 6, "sha256": sha.hexdigest(),
    }
    return validate_receipt(receipt)


def execute(key: str, output: Path, registry: Path) -> dict[str, int]:
    if key != "peppercarrot:26":
        raise BatchError("Source key not approved for real acquisition")
    from .peppercarrot import download_episode_26
    return download_episode_26(output, registry)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Strictly allowlisted licensed-manga batch operations")
    cmds = parser.add_subparsers(dest="command", required=True)
    prepare = cmds.add_parser("prepare")
    prepare.add_argument("--selection", required=True)
    run = cmds.add_parser("download")
    run.add_argument("--key", required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--ids", type=Path, required=True)
    receipt = cmds.add_parser("receipt")
    receipt.add_argument("--key", required=True)
    receipt.add_argument("--export", type=Path, required=True)
    receipt.add_argument("--run-id", type=int, required=True)
    receipt.add_argument("--artifact-id", type=int, required=True)
    receipt.add_argument("--artifact-url", required=True)
    receipt.add_argument("--output", type=Path, required=True)
    combine = cmds.add_parser("consolidate")
    combine.add_argument("--expected-json", required=True)
    combine.add_argument("--receipts", type=Path, required=True)
    combine.add_argument("--registry", type=Path, default=Path("downloaded_manga.json"))
    combine.add_argument("--markdown", type=Path, default=Path("DOWNLOADED_MANGA.md"))
    combine.add_argument("--status", type=Path, default=Path("manga_batch_status.json"))
    status = cmds.add_parser("check-status")
    status.add_argument("--status", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            selection = parse_selection(args.selection)
            matrix = json.dumps(
                [{"key": key, "slug": key.replace(":", "-")} for key in selection],
                separators=(",", ":"),
            )
            path = os.environ.get("GITHUB_OUTPUT")
            if path:
                with Path(path).open("a", encoding="utf-8") as handle:
                    handle.write("jobs=" + matrix + "\n")
            print(matrix)
        elif args.command == "download":
            print(json.dumps(execute(args.key, args.output, args.ids), sort_keys=True))
        elif args.command == "receipt":
            record = receipt_from_export(args.key, args.export, args.run_id, args.artifact_id, args.artifact_url)
            _atomic_text(args.output, json.dumps(record, indent=2, sort_keys=True) + "\n")
            print("Verified artefact receipt created")
        elif args.command == "consolidate":
            expected = parse_matrix(args.expected_json)
            value = consolidate(args.receipts, expected, args.registry, args.markdown, args.status)
            print(json.dumps(value, sort_keys=True))
        else:
            value = json.loads(args.status.read_text(encoding="utf-8"))
            print(json.dumps(value, sort_keys=True))
            if value.get("missing"):
                return 1
    except (BatchError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Batch failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
