"""Bounded, source-native URL chapter download pilot for *local* use.

MangaKatana itself exposes a "Read offline" option, and an independently
verified client knows its series URLs. Downloads are kept local. Public CI
may run one-chapter ephemeral *technical* probes but NEVER uploads media.
Language cannot be asserted when the source does not label its releases;
quarantine such downloads until separately inspected.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from manga_retriever.relife import ReLIFEError, _inspect_cbz
from scripts.five_manga_catalogue import SOURCES, normalise

MAX_CHAPTER_RANGE = 20
CHAPTERS = re.compile(r"^([1-9][0-9]{0,3})(?:-([1-9][0-9]{0,3}))?$")
MAX_OUTPUT_ARCHIVES = 22
MAX_REPORT_BYTES = 4_000_000


class ChapterPilotError(ValueError):
    """Unverified source URL, failed download or invalid manga images."""


def source_for_url(url: str) -> tuple[str, dict]:
    if not isinstance(url, str) or url.strip() != url or len(url) > 300:
        raise ChapterPilotError("Invalid source URL")
    target = urlsplit(url)
    if (target.scheme != "https" or target.netloc != "mangakatana.com"
            or target.query or target.fragment or target.username or target.password
            or target.port is not None or url.endswith("/download")):
        raise ChapterPilotError("Only five exact, publicly listed MangaKatana series URLs are enabled")
    for slug, source in SOURCES.items():
        if url == source["url"]:
            return slug, source
    raise ChapterPilotError("This series URL has not been approved for the local pilot")


def chapter_selection(chapters: str, expected: int) -> tuple[str, int]:
    """At most twenty numbered main chapters per invocation."""
    m = CHAPTERS.fullmatch(chapters)
    if m is None:
        raise ChapterPilotError("Enter one chapter or a bounded N-M range, not 'all'")
    start = int(m.group(1))
    end = int(m.group(2) or start)
    if not 1 <= start <= end <= expected or end - start + 1 > MAX_CHAPTER_RANGE:
        raise ChapterPilotError("Invalid chapter selection; maximum twenty at a time")
    return (f"{start}-{end}" if start != end else str(start)), end - start + 1


def _safe_destination(path: Path) -> None:
    if path.is_symlink() or path.exists():
        raise ChapterPilotError("Destination already exists; never overwrite downloaded media")
    if any(parent.is_symlink() for parent in path.parents):
        raise ChapterPilotError("Output cannot be placed below a symlink")
    if not path.parent.is_dir():
        raise ChapterPilotError("Output parent directory must exist")


def _client_path(value: str) -> str:
    candidate = shutil.which(value)
    if not candidate and Path(value).is_file():
        candidate = str(Path(value).resolve())
    if candidate is None or not Path(candidate).is_file():
        raise ChapterPilotError("Install manga-downloader v25.3.0 or supply its executable")
    return candidate


def _listing(source_url: str, client: str, *, run=subprocess.run) -> dict:
    result = run([client, "list", "--json", source_url], capture_output=True,
                 text=True, timeout=150, check=False)
    if result.returncode != 0 or len(result.stdout) > MAX_REPORT_BYTES:
        raise ChapterPilotError("Chapter listing unavailable; refusing to guess availability")
    try:
        record = json.loads(result.stdout)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ChapterPilotError("Downloader supplied invalid chapter metadata") from exc
    if not isinstance(record, dict) or not isinstance(record.get("chapters"), list):
        raise ChapterPilotError("Unrecognised chapter listing format")
    return record


def _check_listing(slug: str, data: dict, selection: str) -> dict:
    source = SOURCES[slug]
    name = data.get("title")
    if not isinstance(name, str) or normalise(name) not in {
            normalise(a) for a in source["aliases"]}:
        raise ChapterPilotError("Site edition title does not match the requested manga")
    chapters = data["chapters"]
    if not chapters or len(chapters) > 1500:
        raise ChapterPilotError("Empty or excessive chapter catalogue")
    desired, count = chapter_selection(selection, source["expectedMain"])
    a, _, b = desired.partition("-")
    start, end = int(a), int(b) if b else int(a)
    found: set[int] = set()
    languages = set()
    locked: set[int] = set()
    unlabelled = False
    for chapter in chapters:
        if not isinstance(chapter, dict):
            raise ChapterPilotError("Malformed chapter metadata")
        n = chapter.get("number")
        if isinstance(n, bool) or not isinstance(n, (int, float)):
            continue
        if int(n) != n or not start <= int(n) <= end:
            continue
        language = chapter.get("language")
        if language is None or language == "":
            unlabelled = True
        elif isinstance(language, str):
            languages.add(language.casefold())
        else:
            raise ChapterPilotError("Unknown chapter language format")
        if chapter.get("locked") is True:
            locked.add(int(n))
        else:
            found.add(int(n))
    if found != set(range(start, end + 1)):
        raise ChapterPilotError("Requested chapters are missing or locked in the listing")
    if languages and languages != {"en"}:
        raise ChapterPilotError("Source has non-English or mixed-language chapter records")
    return {
        "slug": slug, "sourceTitle": name, "selectedChapters": desired,
        "requestedMainChapters": count,
        "sourceHasExplicitEnglishLabels": languages == {"en"} and not unlabelled,
        "requiresManualEnglishReview": unlabelled or not languages,
    }


def planned_command(client: str, url: str, chapters: str, output: Path) -> list[str]:
    slug, source = source_for_url(url)
    selection, _ = chapter_selection(chapters, source["expectedMain"])
    return [
        client, "--format", "cbz", "--convert-images", "none",
        "--skip-existing", "--language", "en",
        "--output-dir", str(output), "--concurrency", "1",
        "--concurrency-pages", "2", url, selection,
    ]


def inspect_media(folder: Path, *, max_archives: int) -> dict:
    if not folder.is_dir() or folder.is_symlink():
        raise ChapterPilotError("No images downloaded")
    files = list(folder.rglob("*"))
    if any(p.is_symlink() for p in files):
        raise ChapterPilotError("Symlink in downloaded manga output")
    archives = [p for p in files if p.is_file() and p.suffix.casefold() == ".cbz"]
    if not archives or len(archives) > max_archives:
        raise ChapterPilotError("No CBZ files or an excessive number of chapters")
    if any(p.is_file() and p.suffix.casefold() != ".cbz"
           and p.name != "download-report.json" for p in files):
        raise ChapterPilotError("Unexpected files mixed with downloaded chapters")
    checks = []
    try:
        for cbz in sorted(archives):
            inspection = _inspect_cbz(cbz)
            if inspection["verifiedPageCount"] <= 0:
                raise ChapterPilotError("Downloaded chapter contained zero valid image pages")
            checks.append({
                "filename": cbz.name, "pages": inspection["verifiedPageCount"],
                "bytes": cbz.stat().st_size, "sha256": inspection["sha256"],
            })
    except (ReLIFEError, OSError, KeyError, TypeError) as exc:
        raise ChapterPilotError("Downloaded chapter archive was corrupt or unsafe") from exc
    return {"verifiedArchiveCount": len(checks),
            "verifiedPages": sum(x["pages"] for x in checks),
            "archives": checks}


def run_pilot(
    url: str,
    chapters: str,
    destination: Path,
    *,
    client: str = "manga-downloader",
    acknowledge_local_rights: bool = False,
    runner=subprocess.run,
) -> dict:
    """Download into a NEW local folder; report only on success.

    The source's human-readable language is *not* inferred from a title or
    publication synopsis. Where a site provides no language tags, output is
    quarantined pending English-page inspection.
    """
    if not acknowledge_local_rights:
        raise ChapterPilotError("Confirm source export permission and local use before acquisition")
    slug, source = source_for_url(url)
    selection, selected_count = chapter_selection(chapters, source["expectedMain"])
    _safe_destination(destination)
    executable = _client_path(client)
    record = _listing(url, executable, run=runner)
    status = _check_listing(slug, record, selection)
    if destination.exists():
        raise ChapterPilotError("Output appeared while checking source")
    # Temporary sibling prevents incomplete downloads being presented as finished.
    stage = Path(tempfile.mkdtemp(prefix=".manga-url-pilot-", dir=destination.parent))
    try:
        argv = planned_command(executable, url, selection, stage)
        result = runner(argv, capture_output=True, text=True,
                        check=False, timeout=420)
        if result.returncode != 0:
            raise ChapterPilotError("Downloader failed; no completed CBZ published")
        media = inspect_media(stage, max_archives=MAX_OUTPUT_ARCHIVES)
        if media["verifiedArchiveCount"] < selected_count:
            raise ChapterPilotError("Fewer verified chapter archives than requested")
        report = {
            "schemaVersion": 1,
            "sourceType": "mangakatana-local-offline-download",
            "status": "verified-image-files-needs-english-review"
            if status["requiresManualEnglishReview"] else "verified-image-files",
            **status, **media,
            "sourceUrl": url,
            "rightsCheckedByUserNotIndependentlyVerified": True,
            "publicCIArtifactPermitted": False,
            "huggingFaceUploaded": False,
            "retrievedAt": datetime.now(UTC).isoformat(),
        }
        # Report is inside this new staging folder, so publication is atomic.
        (stage / "download-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if destination.exists() or destination.is_symlink():
            raise ChapterPilotError("Output appeared during download")
        stage.replace(destination)
        return report
    finally:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Download authorised English manga chapter URLs LOCALLY")
    p.add_argument("--url", required=True, help="Approved MangaKatana series URL")
    p.add_argument("--chapters", default="1", help="One chapter or N-M, maximum 20")
    p.add_argument("--output", type=Path, required=True, help="New output folder; no overwrite")
    p.add_argument("--client", default="manga-downloader")
    p.add_argument("--acknowledge-local-rights", action="store_true")
    args = p.parse_args(argv)
    try:
        record = run_pilot(args.url, args.chapters, args.output, client=args.client,
                           acknowledge_local_rights=args.acknowledge_local_rights)
    except (ChapterPilotError, OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"Manga URL acquisition failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({k: record[k] for k in
                      ("status", "slug", "selectedChapters", "verifiedArchiveCount",
                       "verifiedPages", "requiresManualEnglishReview")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
