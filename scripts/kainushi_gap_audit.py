"""Read-only English chapter gap inventory for Kainushi wa Akuma.

Contrasts pinned MangaDex English-feed records with a previously observed
56-entry alternative English listing. Counts do NOT establish unique missing
chapters or authorisation to download artwork. No image bytes or uploads.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from manga_retriever.publication_metadata import SOURCE_TITLES
from scripts.source_probe_eight import MangaDexMetadata, summarise

SLUG = "kainushi-wa-akuma"
ALT_ENGLISH_LISTING_COUNT = 56


def audit(client: MangaDexMetadata) -> dict:
    ident = SOURCE_TITLES[SLUG]["sourceId"]
    total, records = client.feed(ident)
    if total != len(records):
        raise ValueError("MangaDex feed was not completely paginated")
    summary = summarise(records)
    return {
        "schemaVersion": 1,
        "slug": SLUG,
        "title": SOURCE_TITLES[SLUG]["name"],
        "source": "MangaDex",
        "sourceMangaId": ident,
        "sourceUrl": f"https://mangadex.org/title/{ident}",
        "status": "metadata-only-not-downloaded",
        "englishFeedEntries": total,
        "mangaDexCoverage": summary,
        "alternativeListing": {
            "sourceUrl": "https://onisaga.com/manga/kainushi-wa-akuma",
            "previouslyObservedEnglishEntries": ALT_ENGLISH_LISTING_COUNT,
            "countDifferenceNotConfirmedMissingChapters": max(0, ALT_ENGLISH_LISTING_COUNT - total),
            "chapterLabelAlignmentVerified": False,
            "downloadRightsVerified": False,
        },
        "imageBytesDownloaded": 0,
        "retrievedAtUtc": datetime.now(UTC).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Compare Kainushi chapter-list metadata")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    if args.output.is_symlink() or args.output.exists():
        p.error("Refusing to replace an existing gap report")
    result = audit(MangaDexMetadata(delay=1.7))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "title": result["title"],
        "englishFeedEntries": result["englishFeedEntries"],
        "alternativeListedEntries": ALT_ENGLISH_LISTING_COUNT,
        "differenceNotVerifiedAsMissing": result["alternativeListing"][
            "countDifferenceNotConfirmedMissingChapters"
        ],
        "imagesDownloaded": 0,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
