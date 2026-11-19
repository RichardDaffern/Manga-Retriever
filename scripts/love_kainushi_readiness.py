"""Read-only readiness verification for Love So Life and Kainushi wa Akuma.

Uses public MangaDex English chapter metadata and chapter image *manifests*;
does not retrieve artwork, page image URLs, or infer redistribution rights.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from scripts.source_probe_eight import MangaDexMetadata

TITLES = {
    "love-so-life": {
        "name": "Love So Life",
        "id": "911a12ae-1022-448e-9219-b7b294d7fb3e",
        "expectedMain": 106,
    },
    "kainushi-wa-akuma": {
        "name": "Kainushi wa Akuma",
        "id": None,
        "expectedMain": None,
    },
}
NUMBER = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z")
MAX_SAMPLE_CHAPTERS = 3


# A separately indexed public reader's chapter-label snapshot, 20 November 2026.
# It is a research comparison, not a permission grant or authoritative edition.
KAINUSHI_EXTERNAL_LABELS = (
    "1 1.1 1.2 2 3 3.1 3.2 4 4.1 4.2 5 5.1 5.2 6 6.1 6.2 7 7.1 7.2 8 8.1 8.2 9 9.1 9.2 9.5 10.1 10.2 11.1 "
    "11.2 11.3 12.1 12.2 13.1 13.2 14.1 14.2 15.1 15.2 16 16.1 16.2 17 18 18.1 18.2 19 20 21 21.5 22 23 "
    "23.5 24 25 25.5"
).split()


def external_label_difference(available_labels: list[str], reference: list[str]) -> dict:
    """Compare raw chapter labels without treating 1.1 and 1 as the same release."""
    provided = set(available_labels)
    indexed = set(reference)
    key = lambda s: (Decimal(s), s)
    return {
        "externalLabelCount": len(indexed),
        "mangaDexLabelCount": len(provided),
        "labelsMissingFromMangaDex": sorted(indexed - provided, key=key),
        "labelsAbsentFromExternalIndex": sorted(provided - indexed, key=key),
        "source": "https://onisaga.com/manga/kainushi-wa-akuma",
        "caveat": "Snapshot of an independent reader index, not authenticated against original volumes",
    }


def labels_from_feed(entries: list[dict]) -> dict:
    """Count all raw chapter labels; never reinterpret decimals as integer chapters."""
    labelled: dict[str, list[dict]] = defaultdict(list)
    blanks = 0
    for chapter in entries:
        if not isinstance(chapter, dict) or not isinstance(chapter.get("attributes"), dict):
            raise ValueError("Malformed English chapter record")
        label = chapter["attributes"].get("chapter")
        if not isinstance(label, str) or not NUMBER.fullmatch(label):
            blanks += 1
            continue
        if not isinstance(chapter.get("id"), str):
            raise ValueError("Missing source chapter ID")
        labelled[label].append(chapter)
    ordered = sorted(labelled, key=lambda x: (Decimal(x), x))
    numeric = sorted(int(label) for label in ordered if label.isdecimal() and int(label) > 0)
    integer_set = set(numeric)
    maximum = max(numeric, default=0)
    return {
        "labels": ordered,
        "entriesByLabel": labelled,
        "unnumberedEntries": blanks,
        "integerChapterCount": len(integer_set),
        "integerChapterMax": maximum or None,
        "missingIntegerLabelsToMax": [str(n) for n in range(1, maximum + 1) if n not in integer_set],
        "decimalLabels": [x for x in ordered if "." in x],
        "duplicateReleaseLabels": {label: len(labelled[label]) for label in ordered if len(labelled[label]) > 1},
        "externalReaderEntries": sum(bool(ch["attributes"].get("externalUrl")) for chunks in labelled.values() for ch in chunks),
    }


def representative_chapters(summary: dict) -> list[tuple[str, str]]:
    """Sample beginning, middle, end from title feed, preferring hosted records."""
    candidates: list[tuple[str, str]] = []
    for label in summary["labels"]:
        group = summary["entriesByLabel"][label]
        chosen = next((chapter for chapter in group if not chapter["attributes"].get("externalUrl")), group[0])
        candidates.append((label, chosen["id"]))
    if not candidates:
        return []
    indexes = sorted({0, (len(candidates) - 1) // 2, len(candidates) - 1})
    return [candidates[index] for index in indexes[:MAX_SAMPLE_CHAPTERS]]


def summarise_manifest(raw: dict) -> dict:
    """Summarise only filename extensions/counts, never expose host or image paths."""
    if not isinstance(raw, dict) or not isinstance(raw.get("chapter"), dict):
        raise ValueError("Malformed MangaDex chapter manifest")
    chapter = raw["chapter"]
    originals = chapter.get("data")
    saver = chapter.get("dataSaver")
    if not isinstance(originals, list) or not isinstance(saver, list):
        raise ValueError("Missing original or data-saver manifest")
    if any(not isinstance(filename, str) or len(filename) > 300 for filename in originals + saver):
        raise ValueError("Unexpected manifest filenames")
    ext = Counter(Path(filename).suffix.lower() for filename in originals)
    return {
        "originalPaths": len(originals),
        "dataSaverPaths": len(saver),
        "matchingPageCounts": len(originals) == len(saver),
        "originalExtensions": dict(sorted(ext.items())),
        "qualityLimit": "File paths alone cannot establish actual pixel dimensions or image quality",
    }


def evaluate(title_key: str, client: MangaDexMetadata) -> dict:
    config = TITLES[title_key]
    if config["id"]:
        identifier = config["id"]
    else:
        selected, matches = client.discover({"name": config["name"],
                                             "aliases": [config["name"]],
                                             "queries": [config["name"]]})
        if selected is None:
            return {"title": config["name"], "status": "title-ambiguous" if matches else "title-not-found",
                    "numberOfExactTitleCandidates": len(matches), "downloadAuthorised": False}
        identifier = selected["id"]
    total, chapters = client.feed(identifier)
    if total != len(chapters):
        raise ValueError("Incomplete English chapter feed")
    groups = labels_from_feed(chapters)
    samples = []
    for label, chapter_id in representative_chapters(groups):
        try:
            manifest = client.request("/at-home/server/" + chapter_id)
            sample = {"chapter": label, **summarise_manifest(manifest), "status": "checked"}
        except (OSError, ValueError, KeyError, TypeError) as exc:
            sample = {"chapter": label, "status": "manifest-unavailable", "reason": str(exc)[:120]}
        samples.append(sample)
    expected = config["expectedMain"]
    numbers = {int(v) for v in groups["labels"] if v.isdecimal() and int(v) > 0}
    missing_expected = [n for n in range(1, expected + 1) if n not in numbers] if expected else None
    external = external_label_difference(groups["labels"], KAINUSHI_EXTERNAL_LABELS) if title_key == "kainushi-wa-akuma" else None
    return {
        "title": config["name"],
        "status": "feed-reviewed",
        "mangaDexId": identifier,
        "titleUrl": "https://mangadex.org/title/" + identifier,
        "externalChapterLabelComparison": external,
        "englishFeedEntries": total,
        "uniqueRawLabels": len(groups["labels"]),
        "integerChapterCount": groups["integerChapterCount"],
        "integerChapterMax": groups["integerChapterMax"],
        "missingIntegerLabelsToMax": groups["missingIntegerLabelsToMax"],
        "expectedMainChaptersFromEarlierAudit": expected,
        "missingExpectedMainNumbers": missing_expected,
        "decimalChapterLabels": groups["decimalLabels"],
        "duplicateReleaseLabels": groups["duplicateReleaseLabels"],
        "unnumberedEntries": groups["unnumberedEntries"],
        "externalReaderEntries": groups["externalReaderEntries"],
        "sampleImageManifests": samples,
        "chapterLabelToVolume": [
            {"label": label, "volumes": sorted({str(ch["attributes"].get("volume") or "?") for ch in group})}
            for label, group in groups["entriesByLabel"].items()
        ],
        "downloadAuthorised": False,
        "publicMediaArtefactAuthorised": False,
        "warning": "MangaDex metadata is not a licence from author, publisher or scanlation groups",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Metadata-only bilingual manga quality/source readiness check")
    parser.add_argument("--output", type=Path, default=Path("reports/love-kainushi-readiness.json"))
    args = parser.parse_args(argv)
    client = MangaDexMetadata(delay=2)
    results = {}
    for key in TITLES:
        print(f"Checking {TITLES[key]['name']} English feed and three chapter manifests", flush=True)
        results[key] = evaluate(key, client)
        print(f"  {results[key]['status']}, {results[key].get('englishFeedEntries')} English entries", flush=True)
    report = {
        "schemaVersion": 1,
        "checkedAtUtc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artworkBytesDownloaded": 0,
        "publisherMasterResolutionVerified": False,
        "sourcePolicy": "https://gitlab.com/mangadex-pub/mangadex-api-docs/-/blob/main/index.md",
        "rightsOutcome": ("MangaDex API requires MangaDex/scanlator credit, scanlator removal compliance "
                          "and no advertising or paid service; it does not license copyrighted chapter rehosting."),
        "titles": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Wrote", args.output, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
