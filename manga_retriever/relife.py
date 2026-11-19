"""ReLIFE-only, local MangaDex CBZ workflow and strict offline page audit.

The external downloader remains the network client. No DRM bypass, source
scraping or public CI media publication is implemented here. Rights remain
with the original creator, publishers and each scanlation group.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from .importer import MAX_CHAPTER, MAX_IMAGE, MIME, ImportFailure, _safe_member, _validate_image

TITLE = "ReLIFE"
TITLE_URL = "https://mangadex.org/title/6e3553b9-ddb5-4d37-b7a3-99998044774e/relife"
EXPECTED_NUMBERED_CHAPTERS = 222
MAX_ARCHIVES = 500
MAX_ARCHIVE_PAGES = 1000
MAX_AUDIT_BYTES = 5_000_000_000


class ReLIFEError(ValueError):
    """Unsafe archive, unavailable command, missing permission, or incomplete download."""


def _sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def _inspect_cbz(path: Path) -> dict:
    """Check image signatures, integrity, order, quotas and each archive's SHA."""
    if path.is_symlink() or not path.is_file() or path.suffix.lower() != ".cbz":
        raise ReLIFEError("Unsafe or non-CBZ chapter archive")
    size = path.stat().st_size
    if not 1 <= size <= MAX_CHAPTER:
        raise ReLIFEError("Chapter archive exceeds quota or is empty")
    pages = []
    seen: set[str] = set()
    image_total = 0
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if not 1 <= len(infos) <= MAX_ARCHIVE_PAGES + 1:
                raise ReLIFEError("Archive has too many files")
            for entry in infos:
                _safe_member(entry.filename[:-1] if entry.is_dir() else entry.filename)
                if entry.is_dir():
                    continue
                name = entry.filename.casefold()
                if name in seen:
                    raise ReLIFEError("Duplicate archive member")
                seen.add(name)
                flags = stat.S_IFMT(entry.external_attr >> 16)
                if flags not in (0, stat.S_IFREG) or entry.flag_bits & 1:
                    raise ReLIFEError("Special or encrypted chapter entry")
                if entry.filename.casefold() == "comicinfo.xml":
                    if entry.file_size > 256_000:
                        raise ReLIFEError("Oversized CBZ metadata")
                    continue
                if Path(entry.filename).suffix.lower() not in MIME:
                    raise ReLIFEError("Unsupported chapter entry (only images and ComicInfo.xml)")
                if not 1 <= entry.file_size <= MAX_IMAGE:
                    raise ReLIFEError("Page exceeds image quota")
                if entry.file_size > max(1, entry.compress_size) * 100:
                    raise ReLIFEError("Suspicious archive compression ratio")
                with archive.open(entry) as image:
                    data = image.read(MAX_IMAGE + 1)
                if len(data) != entry.file_size:
                    raise ReLIFEError("Truncated archive page")
                try:
                    meta = _validate_image(data, entry.filename)
                except ImportFailure as exc:
                    raise ReLIFEError("Invalid manga page image") from exc
                image_total += len(data)
                if image_total > MAX_CHAPTER:
                    raise ReLIFEError("Chapter image-byte quota exceeded")
                pages.append({"name": entry.filename, "sha256": meta["sha256"],
                              "width": meta["width"], "height": meta["height"],
                              "mimeType": meta["mimeType"], "byteSize": len(data)})
    except (OSError, zipfile.BadZipFile, RuntimeError, EOFError, ValueError) as exc:
        if isinstance(exc, ReLIFEError):
            raise
        raise ReLIFEError("Unverifiable CBZ archive") from exc
    if not pages:
        raise ReLIFEError("Chapter archive has no verified pages")
    return {"name": path.name, "sha256": _sha256(path), "archiveByteSize": size,
            "pages": pages, "verifiedPageCount": len(pages)}


def audit_download(directory: Path) -> dict:
    """Audit a local folder without network access; fail closed on any corruption."""
    if directory.is_symlink() or not directory.is_dir():
        raise ReLIFEError("Missing or symlinked ReLIFE download directory")
    if any(path.is_symlink() for path in directory.rglob("*")):
        raise ReLIFEError("Symlinks inside downloaded manga are forbidden")
    archives = sorted(directory.rglob("*.cbz"), key=lambda p: str(p.relative_to(directory)).casefold())
    if not 1 <= len(archives) <= MAX_ARCHIVES:
        raise ReLIFEError("No CBZs found or archive count exceeds limit")
    byte_total = sum(p.stat().st_size for p in archives)
    if byte_total > MAX_AUDIT_BYTES:
        raise ReLIFEError("Total downloaded file size exceeds audit limit")
    reports = []
    seen_names = set()
    for archive in archives:
        relative = archive.relative_to(directory).as_posix()
        if relative.casefold() in seen_names:
            raise ReLIFEError("Case-folding archive path collision")
        seen_names.add(relative.casefold())
        record = _inspect_cbz(archive)
        record["relativePath"] = relative
        reports.append(record)
    all_pages = [page for report in reports for page in report["pages"]]
    return {
        "schemaVersion": 1,
        "title": TITLE,
        "sourceTitleUrl": TITLE_URL,
        "sourceEdition": "MangaDex English uploader-provided images; not publisher masters",
        "requestedQuality": "source-original-not-data-saver",
        "completeSeriesVerified": False,
        "completenessNote": "A local CBZ audit cannot prove every one of the 222 numbered chapters or extras is available.",
        "verifiedArchives": len(reports),
        "verifiedPages": len(all_pages),
        "totalArchiveBytes": byte_total,
        "minWidth": min(page["width"] for page in all_pages),
        "maxWidth": max(page["width"] for page in all_pages),
        "minHeight": min(page["height"] for page in all_pages),
        "maxHeight": max(page["height"] for page in all_pages),
        "archives": reports,
    }


def _safe_output(directory: Path) -> None:
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise ReLIFEError("Output must be a normal directory")
    for parent in [directory, *directory.parents]:
        if parent.is_symlink():
            raise ReLIFEError("Output may not be under a symlink")


def planned_command(output: Path, start: int, end: int) -> list[str]:
    """Prepare fixed MangaDex title and original-quality command, never arbitrary URLs."""
    if not 1 <= start <= end <= EXPECTED_NUMBERED_CHAPTERS:
        raise ReLIFEError("Chapter selection must be between 1 and 222")
    _safe_output(output)
    return [
        sys.executable, "-m", "mangadex_downloader", TITLE_URL,
        "--language", "en", "--save-as", "cbz", "--path", str(output),
        "--start-chapter", str(start), "--end-chapter", str(end),
        "--order", "oldest", "--http-retries", "3", "--delay-requests", "2",
    ]


def download(output: Path, start: int, end: int, *, acknowledge_rights: bool,
             run=subprocess.run, module_exists=importlib.util.find_spec) -> None:
    """Run user-installed local client; content and caches stay on their computer."""
    if not acknowledge_rights:
        raise ReLIFEError("Confirm authorised personal use and source terms with --acknowledge-rights")
    argv = planned_command(output, start, end)
    if module_exists("mangadex_downloader") is None:
        raise ReLIFEError("Install the maintained client first: py -3.12 -m pip install mangadex-downloader==3.1.4")
    output.mkdir(parents=True, exist_ok=True)
    # No shell, no credentials, no proxies, no bypass flags, and never writes to GitHub Actions.
    result = run(argv, check=False)
    if result.returncode:
        raise ReLIFEError("Downloader failed; partial files may remain locally for inspection/resume")


def _write_report(output: Path, contents: dict) -> None:
    _safe_output(output.parent)
    if output.is_symlink():
        raise ReLIFEError("Cannot overwrite a linked report")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=output.parent, prefix=".relife-report-", suffix=".json")
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(contents, file, ensure_ascii=False, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp, output)
    finally:
        tmp.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ReLIFE only: highest available English CBZ quality, local use")
    parser.add_argument("--mode", choices=["pilot", "full", "audit"], default="pilot")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--acknowledge-rights", action="store_true",
                        help="You have checked local personal-use rights and source terms")
    args = parser.parse_args(argv)
    try:
        if args.mode != "audit":
            start, end = (1, 2) if args.mode == "pilot" else (1, EXPECTED_NUMBERED_CHAPTERS)
            download(args.output, start, end, acknowledge_rights=args.acknowledge_rights)
        result = audit_download(args.output)
        result["auditedAt"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        report = args.report or args.output.parent / "relife_quality_audit.json"
        _write_report(report, result)
        print(json.dumps({"status": "verified-local-cbz", "chapters": result["verifiedArchives"],
                          "pages": result["verifiedPages"], "report": str(report)}, sort_keys=True))
    except (ReLIFEError, ImportFailure, OSError, ValueError) as exc:
        print(f"ReLIFE acquisition or verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
