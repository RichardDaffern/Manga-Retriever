"""Parallel, resumable private Windows manga batch downloader.

Uses only five pinned MangaKatana URLs with the chapter-CBZ validator.
Does not upload private manga pages to public Actions or Hugging Face.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from scripts.five_manga_catalogue import SOURCES
from scripts.local_url_manga_download import (
    ChapterPilotError,
    inspect_media,
    run_pilot,
)

MAX_WORKERS = 2
BATCH_SIZE = 20


def chunks(first: int, last: int, size: int = BATCH_SIZE) -> list[tuple[int, int]]:
    if not 1 <= first <= last <= 3000 or not 1 <= size <= BATCH_SIZE:
        raise ChapterPilotError("Invalid bounded chapter batch request")
    return [(s, min(s + size - 1, last)) for s in range(first, last + 1, size)]


def _validated_existing(folder: Path, slug: str, selection: str) -> dict:
    report = folder / "download-report.json"
    if folder.is_symlink() or report.is_symlink() or not report.is_file():
        raise ChapterPilotError("An existing batch has no verified report")
    if report.stat().st_size > 1_000_000:
        raise ChapterPilotError("Unexpectedly large batch report")
    data = json.loads(report.read_text(encoding="utf-8"))
    if (data.get("slug") != slug or data.get("selectedChapters") != selection
            or not isinstance(data.get("verifiedPages"), int)
            or data["verifiedPages"] <= 0):
        raise ChapterPilotError("Existing batch report does not match this title or selection")
    media = inspect_media(folder, max_archives=BATCH_SIZE + 2)
    if media["verifiedPages"] != data["verifiedPages"]:
        raise ChapterPilotError("Existing batch images differ from verified report")
    return {"selection": selection, "status": "already-verified", "pages": media["verifiedPages"]}


def _one_title(
    slug: str,
    output_root: Path,
    client: str,
    mode: str,
) -> dict:
    source = SOURCES[slug]
    max_chapter = 1 if mode == "pilot" else source["expectedMain"]
    target = output_root / slug
    if target.is_symlink():
        raise ChapterPilotError("Unsafe manga title directory")
    target.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    for start, end in chunks(1, max_chapter):
        label = str(start) if start == end else f"{start}-{end}"
        output = target / f"chapters-{label}"
        try:
            if output.exists() or output.is_symlink():
                records.append(_validated_existing(output, slug, label))
                continue
            report = run_pilot(
                source["url"],
                label,
                output,
                client=client,
                acknowledge_local_rights=True,
            )
            records.append({
                "selection": label,
                "status": report["status"],
                "pages": report["verifiedPages"],
                "verifiedCBZ": report["verifiedArchiveCount"],
                "requiresManualEnglishReview": report["requiresManualEnglishReview"],
            })
        except (ChapterPilotError, OSError, ValueError, RuntimeError) as exc:
            records.append({"selection": label, "status": "failed",
                            "error": str(exc)[:240]})
            break  # Other titles continue, but stop failed title to reduce source load.
    return {
        "slug": slug,
        "title": source["title"],
        "status": "passed" if all(item["status"] != "failed" for item in records) else "partial",
        "batches": records,
        "verifiedPages": sum(item.get("pages", 0) for item in records),
        "verifiedBatchCount": sum(item["status"] != "failed" for item in records),
        "expectedMainChapters": source["expectedMain"],
        "mediaRemainsLocal": True,
        "huggingFaceUploaded": False,
    }


def run_bulk(
    slugs: list[str],
    output_root: Path,
    *,
    client: str = "manga-downloader",
    mode: str = "pilot",
    workers: int = 2,
    acknowledge_local_rights: bool = False,
    confirm_english_reviewed: bool = False,
) -> dict:
    if not acknowledge_local_rights:
        raise ChapterPilotError("Check source terms and authorise local downloads first")
    if mode not in ("pilot", "full"):
        raise ChapterPilotError("Unknown download mode")
    if mode == "full" and not confirm_english_reviewed:
        raise ChapterPilotError("Full-series download requires review of actual English chapter pages")
    if type(workers) is not int or not 1 <= workers <= MAX_WORKERS:
        raise ChapterPilotError("Use one or two independent source workers")
    if not slugs or len(set(slugs)) != len(slugs) or any(s not in SOURCES for s in slugs):
        raise ChapterPilotError("Select one or more unique approved manga source slugs")
    if output_root.is_symlink() or not output_root.is_dir():
        raise ChapterPilotError("Create a real output directory first, outside the repository")
    if any(parent.is_symlink() for parent in output_root.parents):
        raise ChapterPilotError("Unsafe symlink in output path")
    with ThreadPoolExecutor(max_workers=min(workers, len(slugs))) as pool:
        jobs = {pool.submit(_one_title, slug, output_root, client, mode): slug for slug in slugs}
        results = {}
        for job in as_completed(jobs):
            slug = jobs[job]
            try:
                results[slug] = job.result()
            except Exception as exc:
                results[slug] = {"slug": slug, "status": "partial",
                                 "error": str(exc)[:240], "batches": []}
    report = {
        "schemaVersion": 1,
        "mode": mode,
        "status": "verified-local-batches"
        if all(item["status"] == "passed" for item in results.values())
        else "partial",
        "titles": [results[s] for s in slugs],
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "publicMediaArtifacts": False,
        "ownerConfirmedEnglishForFull": confirm_english_reviewed if mode == "full" else False,
    }
    # An updated report may replace a previous *report*, never downloaded media.
    fd, name = tempfile.mkstemp(prefix=".manga-bulk-", suffix=".json", dir=output_root)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
            file.write("\n")
        os.replace(name, output_root / "manga-bulk-status.json")
    finally:
        Path(name).unlink(missing_ok=True)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download real manga CBZs locally in parallel")
    parser.add_argument("--slugs", default="all",
                        help="Comma-separated source keys or 'all' for the five approved manga")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--client", default="manga-downloader")
    parser.add_argument("--acknowledge-local-rights", action="store_true")
    parser.add_argument("--confirm-english-reviewed", action="store_true")
    args = parser.parse_args(argv)
    chosen = list(SOURCES) if args.slugs == "all" else args.slugs.split(",")
    try:
        report = run_bulk(
            chosen, args.output_root, client=args.client, mode=args.mode,
            workers=args.workers,
            acknowledge_local_rights=args.acknowledge_local_rights,
            confirm_english_reviewed=args.confirm_english_reviewed,
        )
    except (ChapterPilotError, OSError, ValueError) as exc:
        print(f"Local manga bulk download failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": report["status"],
                      "completedTitles": sum(t["status"] == "passed" for t in report["titles"]),
                      "titles": len(report["titles"]),
                      "verifiedPages": sum(t.get("verifiedPages", 0) for t in report["titles"]),
                      "report": str(args.output_root / "manga-bulk-status.json")}))
    return 0 if report["status"] == "verified-local-batches" else 1


if __name__ == "__main__":
    raise SystemExit(main())
