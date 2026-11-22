"""Bounded MangaDex metadata-only audit for the exact Nisekoi title ID.

This verifies the third-party tracker lead against MangaDex's own API.
It reads title/feed metadata and one chapter's image manifest only. It never
downloads image bytes, creates archives, or asserts rights to retain artwork.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.source_probe_eight import MangaDexMetadata, UUID, normalise, summarise

MANGA_ID = "ce16b1c3-d6bb-41e0-8671-d8b065248ba2"
MANGA_URL = f"https://mangadex.org/title/{MANGA_ID}"
EXPECTED_ENGLISH_TITLES = {"nisekoi", "nisekoi false love"}
EXPECTED_MAIN_CHAPTERS = 229


def audit(client: MangaDexMetadata) -> dict:
    response = client.request(f"/manga/{MANGA_ID}")
    data = response.get("data")
    if (response.get("result") != "ok" or not isinstance(data, dict)
            or data.get("id") != MANGA_ID or data.get("type") != "manga"):
        raise ValueError("MangaDex title response does not match the exact Nisekoi UUID")

    attrs = data.get("attributes")
    if not isinstance(attrs, dict):
        raise ValueError("Invalid MangaDex title attributes")
    titles = attrs.get("title")
    english_title = titles.get("en") if isinstance(titles, dict) else None
    if (not isinstance(english_title, str)
            or normalise(english_title) not in EXPECTED_ENGLISH_TITLES):
        raise ValueError("MangaDex English title does not exactly identify Nisekoi")

    total, chapters = client.feed(MANGA_ID)
    if total != len(chapters) or total < 0:
        raise ValueError("Incomplete paginated English chapter feed")
    if any(
        not isinstance(item, dict)
        or item.get("attributes", {}).get("translatedLanguage") != "en"
        for item in chapters
    ):
        raise ValueError("Feed contains an entry not labelled English")

    coverage = summarise(chapters)
    first_chapter_id = coverage.pop("firstChapterId")
    manifest = None
    manifest_error = None
    if first_chapter_id:
        try:
            manifest = client.image_manifest(first_chapter_id)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            manifest_error = f"{type(exc).__name__}: {str(exc)[:140]}"

    missing = coverage["missingPositiveNumbers"]
    distinct = coverage["distinctNumberedChapters"]
    numbered_complete = (
        distinct == EXPECTED_MAIN_CHAPTERS
        and coverage["firstNumberedChapter"] == 1
        and coverage["highestNumberedChapter"] == EXPECTED_MAIN_CHAPTERS
        and not missing
    )
    status = "english-metadata-present" if total else "no-english-feed-entries"
    if manifest and manifest.get("originalPagePaths") == 0:
        status = "english-feed-without-hosted-original-page-paths"

    return {
        "schemaVersion": 1,
        "source": "MangaDex",
        "sourceMangaId": MANGA_ID,
        "sourceUrl": MANGA_URL,
        "canonicalEnglishTitle": english_title,
        "originalLanguage": attrs.get("originalLanguage"),
        "publicationStatus": attrs.get("status"),
        "englishFeedEntries": total,
        "numberedCoverage": coverage,
        "expectedMainNumberedChapters": EXPECTED_MAIN_CHAPTERS,
        "numberedMainCoverageComplete": numbered_complete,
        "sampleChapterId": first_chapter_id,
        "sampleOriginalQualityManifest": manifest,
        "sampleManifestError": manifest_error,
        "status": status,
        "metadataOnly": True,
        "chapterImageBytesDownloaded": 0,
        "cbzFilesCreated": 0,
        "pageTextManuallyReviewed": False,
        "rightsToArchiveOrRedistributeVerified": False,
        "eligibleForMediaDownload": False,
        "auditedAtUtc": datetime.now(UTC).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify exact Nisekoi MangaDex metadata without retrieving images"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("Output file exists or is symlinked; refusing to overwrite")

    result = audit(MangaDexMetadata(delay=1.7))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "title": result["canonicalEnglishTitle"],
        "englishFeedEntries": result["englishFeedEntries"],
        "distinctNumberedChapters": result["numberedCoverage"]["distinctNumberedChapters"],
        "missingMainChapters": result["numberedCoverage"]["missingPositiveNumbers"],
        "sampleOriginalPagePaths": (
            result["sampleOriginalQualityManifest"] or {}
        ).get("originalPagePaths"),
        "imageBytesDownloaded": 0,
        "rightsVerified": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
