"""Check actual Korean and all-language MangaDex chapter feeds for one pinned title.

Manga's original language ('ko') is not evidence Korean chapter image files
have been uploaded. This audit fetches no copyrighted media.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

from scripts.source_probe_eight import MangaDexMetadata, summarise

MANGA_ID = "90f7c7a6-b759-4afb-b1cb-1af4660df307"
URL = f"https://mangadex.org/title/{MANGA_ID}"
MAX_CHAPTERS = 800


def _feed(client: MangaDexMetadata, *, language: str | None) -> tuple[int, list[dict]]:
    records = []
    total = None
    for offset in range(0, MAX_CHAPTERS, 100):
        params = [
            ("limit", 100), ("offset", offset),
            *[("contentRating[]", rating)
              for rating in ("safe", "suggestive", "erotica", "pornographic")],
        ]
        if language is not None:
            params.append(("translatedLanguage[]", language))
        payload = client.request(f"/manga/{MANGA_ID}/feed?{urlencode(params)}")
        entries = payload.get("data")
        if not isinstance(entries, list):
            raise ValueError("Invalid chapter feed response")
        if total is None:
            total = payload.get("total")
            if type(total) is not int or not 0 <= total <= MAX_CHAPTERS:
                raise ValueError("Unbounded chapter feed")
        records.extend(entries)
        if len(records) >= total:
            break
    if total is None or len(records) != total:
        raise ValueError("Incomplete feed: cannot claim Korean availability")
    return total, records


def audit(client: MangaDexMetadata) -> dict:
    payload = client.request(f"/manga/{MANGA_ID}")
    manga = payload.get("data")
    if not isinstance(manga, dict) or manga.get("id") != MANGA_ID:
        raise ValueError("MangaDex title UUID mismatch")
    attributes = manga.get("attributes", {})
    if not isinstance(attributes, dict):
        raise ValueError("Missing title attributes")
    original_language = attributes.get("originalLanguage")
    korean_count, korean = _feed(client, language="ko")
    unfiltered_count, unfiltered = _feed(client, language=None)
    languages = {}
    for chapter in unfiltered:
        lang = chapter.get("attributes", {}).get("translatedLanguage")
        if isinstance(lang, str):
            languages[lang] = languages.get(lang, 0) + 1
    if korean_count and not all(c.get("attributes", {}).get("translatedLanguage") == "ko" for c in korean):
        raise ValueError("Unexpected language in Korean feed")
    coverage = summarise(korean)
    chapter_id = coverage.pop("firstChapterId")
    manifest = None
    if chapter_id:
        manifest = client.image_manifest(chapter_id)
    usable = bool(korean_count and manifest and manifest.get("originalPagePaths", 0) > 0)
    return {
        "schemaVersion": 1,
        "title": "Acquainted: Encounter Spin-Off",
        "sourceUrl": URL,
        "mangaDexId": MANGA_ID,
        "originalLanguage": original_language,
        "sourceContentRating": attributes.get("contentRating"),
        "koreanFeedEntries": korean_count,
        "koreanCoverage": coverage,
        "sampleKoreanChapterId": chapter_id,
        "sampleKoreanImageManifest": manifest,
        "unfilteredFeedEntries": unfiltered_count,
        "languagesInVisibleChapterFeed": languages,
        "koreanOriginalImageSourceVerified": usable,
        "downloadStatus": "korean-image-source-candidate" if usable else "no-confirmed-korean-images",
        "mediaBytesDownloaded": 0,
        "mediaPublished": False,
        "auditedAtUtc": datetime.now(UTC).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit exact Korean MangaDex chapter availability")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("Output exists, refusing to replace")
    result = audit(MangaDexMetadata(delay=1.7))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "title", "originalLanguage", "koreanFeedEntries", "unfilteredFeedEntries",
        "languagesInVisibleChapterFeed", "koreanOriginalImageSourceVerified", "downloadStatus",
    )}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
