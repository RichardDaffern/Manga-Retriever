"""Bounded MangaDex metadata-only audit for the six new target manga.

The Nisekoi exact-ID audit already exists, so this run checks the other five
targets only. It queries exact title metadata, English chapter-feed metadata,
and at most one first-chapter image-path manifest per exact edition. It never
fetches image bytes, creates CBZs, or establishes rights to retain artwork.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.source_probe_eight import MangaDexMetadata, summarise, titles_for

TARGETS = [
    {
        "name": "Kimi no Iru Machi",
        "queries": ["Kimi no Iru Machi", "A Town Where You Live", "君のいる町"],
        "aliases": ["Kimi no Iru Machi", "A Town Where You Live", "君のいる町"],
    },
    {
        "name": "Love Hina",
        "queries": ["Love Hina", "ラブひな"],
        "aliases": ["Love Hina", "ラブひな"],
    },
    {
        "name": "Lovely Complex",
        "queries": ["Lovely Complex", "Love Com", "ラブ★コン"],
        "aliases": ["Lovely Complex", "Love Com", "LoveCom", "ラブ★コン", "ラブコン"],
    },
    {
        "name": "Mado kara Madoka-chan",
        "queries": ["Mado kara Madoka-chan", "Madoka from the Window", "まどからマドカちゃん"],
        "aliases": ["Mado kara Madoka-chan", "Madoka from the Window", "まどからマドカちゃん"],
    },
    {
        "name": "The Fairytale-like You Goes on the Assault",
        "queries": ["The Fairytale-like You Goes on the Assault", "Hakanai Kimi wa Moukou wo Hajimeru", "儚いキミは猛攻をはじめる"],
        "aliases": [
            "The Fairytale-like You Goes on the Assault",
            "The Fairytale-Like You Goes On The Assault",
            "Hakanai Kimi wa Moukou wo Hajimeru",
            "儚いキミは猛攻をはじめる",
        ],
    },
]


def audit_candidate(candidate: dict, client: MangaDexMetadata) -> dict:
    manga_id = candidate["id"]
    attributes = candidate.get("attributes")
    if not isinstance(attributes, dict):
        raise ValueError("MangaDex title attributes are missing")
    title_variants = attributes.get("title")
    if not isinstance(title_variants, dict):
        title_variants = {}
    result = {
        "mangaDexId": manga_id,
        "sourceUrl": f"https://mangadex.org/title/{manga_id}",
        "titles": titles_for(candidate),
        "originalLanguage": attributes.get("originalLanguage"),
        "publicationStatus": attributes.get("status"),
        "englishTitleMetadataPresent": (
            isinstance(title_variants.get("en"), str)
            and bool(title_variants.get("en", "").strip())
        ),
        "allTitleVariants": title_variants,
        "englishFeedEntries": None,
        "numberedCoverage": None,
        "sampleImageManifest": None,
        "sampleManifestError": None,
        "metadataOnly": True,
        "imageBytesDownloaded": 0,
        "cbzFilesCreated": 0,
        "pageTextManuallyReviewed": False,
        "rightsToArchiveOrRedistributeVerified": False,
        "eligibleForMediaDownload": False,
    }
    try:
        total, chapters = client.feed(manga_id)
        if type(total) is not int or total != len(chapters) or total < 0:
            raise ValueError("Incomplete paginated English chapter feed")
        if any(
            not isinstance(item, dict)
            or item.get("attributes", {}).get("translatedLanguage") != "en"
            for item in chapters
        ):
            raise ValueError("English feed contains an entry not labelled English")

        coverage = summarise(chapters)
        first_chapter_id = coverage.pop("firstChapterId")
        result["englishFeedEntries"] = total
        result["numberedCoverage"] = coverage
        result["status"] = "english-feed-metadata-present" if total else "no-english-feed-entries"
        if first_chapter_id:
            try:
                manifest = client.image_manifest(first_chapter_id)
                result["sampleImageManifest"] = manifest
                if manifest.get("originalPagePaths") == 0:
                    result["status"] = "english-feed-without-hosted-original-pages"
            except (OSError, ValueError, TypeError, KeyError) as exc:
                result["sampleManifestError"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        return result
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result["status"] = "source-check-failed"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        return result


def audit_target(work: dict, client: MangaDexMetadata) -> dict:
    result = {
        "name": work["name"],
        "source": "MangaDex",
        "status": "not-found",
        "sourceUrl": None,
        "mangaDexId": None,
        "candidateMatches": [],
        "candidateEditionAudits": [],
        "metadataOnly": True,
        "imageBytesDownloaded": 0,
        "cbzFilesCreated": 0,
        "rightsToArchiveOrRedistributeVerified": False,
        "eligibleForMediaDownload": False,
    }
    try:
        selected, matches = client.discover(work)
        result["candidateMatches"] = [
            {
                "id": item["id"],
                "titles": titles_for(item),
                "originalLanguage": item.get("attributes", {}).get("originalLanguage"),
            }
            for item in matches[:10]
        ]
        if selected is None:
            if matches:
                result["status"] = "ambiguous-exact-title"
                # Inspect each exact edition independently, but never choose one silently.
                result["candidateEditionAudits"] = [
                    audit_candidate(item, client) for item in matches[:5]
                ]
            return result

        result.update(audit_candidate(selected, client))
        return result
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result["status"] = "source-check-failed"
        result["error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
        return result


def run_audit(client: MangaDexMetadata | None = None) -> dict:
    api = client or MangaDexMetadata(delay=1.7)
    results = []
    for work in TARGETS:
        print(f"Checking MangaDex metadata for {work['name']}...", flush=True)
        result = audit_target(work, api)
        results.append(result)
        candidate_feeds = [
            edition.get("englishFeedEntries")
            for edition in result.get("candidateEditionAudits", [])
        ]
        print(
            f"  {result['status']} / English feed entries: "
            f"{result.get('englishFeedEntries')} / candidate feeds: {candidate_feeds}",
            flush=True,
        )
    return {
        "schemaVersion": 1,
        "checkedAtUtc": datetime.now(UTC).isoformat(),
        "method": (
            "Exact MangaDex title search, paginated translatedLanguage=en feeds, "
            "and at most one first-chapter image-path manifest per exact edition"
        ),
        "titles": results,
        "totals": {
            "titlesChecked": len(results),
            "exactMatches": sum(bool(item["candidateMatches"]) for item in results),
            "withEnglishFeedEntries": sum(
                isinstance(item.get("englishFeedEntries"), int)
                and item["englishFeedEntries"] > 0
                for item in results
            ) + sum(
                isinstance(edition.get("englishFeedEntries"), int)
                and edition["englishFeedEntries"] > 0
                for item in results
                for edition in item.get("candidateEditionAudits", [])
            ),
            "imageBytesDownloaded": 0,
            "cbzFilesCreated": 0,
            "rightsVerified": False,
        },
        "rightsWarning": (
            "MangaDex metadata, English translation labels and image-path manifests do not "
            "grant permission to archive or redistribute the artwork. No media download is authorised."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit MangaDex metadata for five new targets; retrieve no artwork"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("Output file exists or is symlinked; refusing to overwrite")
    report = run_audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["totals"], sort_keys=True))
    return 1 if any(
        item["status"] == "source-check-failed"
        or any(
            edition.get("status") == "source-check-failed"
            for edition in item.get("candidateEditionAudits", [])
        )
        for item in report["titles"]
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main())
