"""Read-only English chapter label reconciliation for Kainushi wa Akuma.

Compares live MangaDex English-feed labels with a dated, explicitly
attributed 56-entry public OniSaga INDEX snapshot. Chapter labels are
metadata. Differences are NOT evidence of missing images, independent
translations or permission to download/redistribute any pages.

OniSaga's reader blocks ordinary HTTP access; this snapshot is taken from its
publicly indexed *chapter list*, not an unverified bulk/scraping download.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from manga_retriever.publication_metadata import SOURCE_TITLES
from scripts.source_probe_eight import MangaDexMetadata, summarise

SLUG = "kainushi-wa-akuma"
ALT_SOURCE_URL = "https://onisaga.com/manga/kainushi-wa-akuma"
ALT_ENGLISH_LISTING_COUNT = 56
ALT_INDEX_SNAPSHOT_DATE = "2026-11-20"
# Publicly indexed labels on 20 Nov 2026. Not a live-feed or media-rights check.
ALT_INDEXED_LABELS = tuple((
    "1 1.1 1.2 2 3 3.1 3.2 4 4.1 4.2 5 5.1 5.2 "
    "6 6.1 6.2 7 7.1 7.2 8 8.1 8.2 9 9.1 9.2 9.5 "
    "10.1 10.2 11.1 11.2 11.3 12.1 12.2 13.1 13.2 "
    "14.1 14.2 15.1 15.2 16 16.1 16.2 17 18 18.1 "
    "18.2 19 20 21 21.5 22 23 23.5 24 25 25.5"
).split())


def _normalise_label(value: object) -> str | None:
    """Canonicalise strict positive integer/fractional labels without rounding."""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,4}(?:\.[0-9]{1,6})?", value):
        return None
    try:
        num = Decimal(value)
    except InvalidOperation:
        return None
    if not num.is_finite() or not 0 < num <= 1000:
        return None
    return format(num.normalize(), "f")


def _sort_labels(labels: set[str]) -> list[str]:
    return sorted(labels, key=lambda value: (Decimal(value), value))


def compare_labels(records: list[dict]) -> dict:
    if len(ALT_INDEXED_LABELS) != ALT_ENGLISH_LISTING_COUNT or len(set(ALT_INDEXED_LABELS)) != len(ALT_INDEXED_LABELS):
        raise ValueError("Reference label snapshot is incomplete or duplicated")
    manga_labels: set[str] = set()
    duplicates: set[str] = set()
    unlabelled = 0
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("attributes"), dict):
            raise ValueError("Malformed MangaDex chapter record")
        label = _normalise_label(record["attributes"].get("chapter"))
        if label is None:
            unlabelled += 1
            continue
        if label in manga_labels:
            duplicates.add(label)
        manga_labels.add(label)
    reference_labels = {_normalise_label(item) for item in ALT_INDEXED_LABELS}
    if None in reference_labels or len(reference_labels) != ALT_ENGLISH_LISTING_COUNT:
        raise ValueError("Invalid public index snapshot")
    return {
        "mangaDexLabels": _sort_labels(manga_labels),
        "publicIndexLabels": _sort_labels(reference_labels),
        "inBothIndexes": _sort_labels(manga_labels & reference_labels),
        "publicIndexOnly": _sort_labels(reference_labels - manga_labels),
        "mangaDexOnly": _sort_labels(manga_labels - reference_labels),
        "duplicatedMangaDexLabels": _sort_labels(duplicates),
        "unlabelledMangaDexEntries": unlabelled,
        "referenceIsLiveOrAuthoritative": False,
        "differenceIndicatesDownloadRights": False,
        "differenceProvesMissingMedia": False,
    }


def audit(client: MangaDexMetadata) -> dict:
    ident = SOURCE_TITLES[SLUG]["sourceId"]
    total, records = client.feed(ident)
    if total != len(records):
        raise ValueError("MangaDex feed was not completely paginated")
    summary = summarise(records)
    comparison = compare_labels(records)
    return {
        "schemaVersion": 1,
        "slug": SLUG,
        "title": SOURCE_TITLES[SLUG]["name"],
        "source": "MangaDex",
        "sourceMangaId": ident,
        "sourceUrl": f"https://mangadex.org/title/{ident}",
        "status": "chapter-labels-reconciled-metadata-only",
        "englishFeedEntries": total,
        "mangaDexCoverage": summary,
        "alternativeListing": {
            "sourceUrl": ALT_SOURCE_URL,
            "previouslyObservedEnglishEntries": ALT_ENGLISH_LISTING_COUNT,
            "sourceSnapshotDate": ALT_INDEX_SNAPSHOT_DATE,
            "sourceIsSearchIndexedChapterLabels": True,
            "countDifferenceNotConfirmedMissingChapters": max(0, ALT_ENGLISH_LISTING_COUNT - total),
            "exactLabelComparison": comparison,
            "chapterLabelAlignmentVerified": False,
            "downloadRightsVerified": False,
        },
        "imageBytesDownloaded": 0,
        "retrievedAtUtc": datetime.now(UTC).isoformat(),
    }


def report_csv(result: dict) -> str:
    from io import StringIO

    comparison = result["alternativeListing"]["exactLabelComparison"]
    mangadex_labels = set(comparison["mangaDexLabels"])
    public_labels = set(comparison["publicIndexLabels"])
    stream = StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["chapterLabel", "mangaDexEnglishFeedListed", "onisagaIndexedListed", "downloadConfirmed"])
    for chapter in _sort_labels(mangadex_labels | public_labels):
        writer.writerow([chapter, str(chapter in mangadex_labels).lower(),
                         str(chapter in public_labels).lower(), "false"])
    return stream.getvalue()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Compare exact Kainushi chapter labels without downloading images")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--csv", type=Path)
    args = p.parse_args(argv)
    if args.output.is_symlink() or args.output.exists() or (args.csv and (args.csv.is_symlink() or args.csv.exists())):
        p.error("Refusing to replace an existing chapter gap report")
    result = audit(MangaDexMetadata(delay=1.7))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        args.csv.write_text(report_csv(result), encoding="utf-8")
    labels = result["alternativeListing"]["exactLabelComparison"]
    print(json.dumps({
        "title": result["title"],
        "englishFeedEntries": result["englishFeedEntries"],
        "alternativeListedEntries": ALT_ENGLISH_LISTING_COUNT,
        "publicIndexOnly": labels["publicIndexOnly"],
        "mangaDexOnly": labels["mangaDexOnly"],
        "differenceDoesNotProveMissingChapters": True,
        "imagesDownloaded": 0,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
