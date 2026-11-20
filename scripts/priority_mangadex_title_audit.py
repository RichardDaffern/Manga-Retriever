"""Priority MangaDex exact-ID audit for owner-selected manga, metadata only.

The user supplied an exact MangaDex title URL. Never infer its title from a
search result or accidentally substitute an identically named edition.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.source_probe_eight import MangaDexMetadata, summarise

MANGA_ID = "90f7c7a6-b759-4afb-b1cb-1af4660df307"
MANGA_URL = f"https://mangadex.org/title/{MANGA_ID}"


def _title(attrs: dict) -> tuple[str, bool]:
    titles = attrs.get("title")
    if not isinstance(titles, dict):
        raise ValueError("The target manga has no readable title metadata")
    name = titles.get("en")
    if isinstance(name, str) and name.strip():
        return name.strip()[:200], True
    for v in titles.values():
        if isinstance(v, str) and v.strip():
            return v.strip()[:200], False
    raise ValueError("The target manga has no readable title metadata")


def audit(client: MangaDexMetadata) -> dict:
    response = client.request(f"/manga/{MANGA_ID}")
    data = response.get("data")
    if (response.get("result") != "ok" or not isinstance(data, dict)
            or data.get("id") != MANGA_ID or data.get("type") != "manga"):
        raise ValueError("MangaDex title response does not match the owner-selected URL")
    attrs = data.get("attributes")
    if not isinstance(attrs, dict):
        raise ValueError("Invalid MangaDex title attributes")
    name, english_title = _title(attrs)
    total, chapters = client.feed(MANGA_ID)
    if total != len(chapters) or total < 0:
        raise ValueError("Incomplete English chapter listing")
    summary = summarise(chapters)
    first_chapter_id = summary.pop("firstChapterId")
    image_manifest = None
    if first_chapter_id:
        try:
            image_manifest = client.image_manifest(first_chapter_id)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            image_manifest = {"status": "unavailable", "error": str(exc)[:150]}
    return {
        "schemaVersion": 1,
        "priority": "high",
        "source": "MangaDex",
        "sourceMangaId": MANGA_ID,
        "sourceUrl": MANGA_URL,
        "canonicalSourceTitle": name,
        "englishTitleConfirmed": english_title,
        "originalLanguage": attrs.get("originalLanguage"),
        "sourcePublicationStatus": attrs.get("status"),
        "englishFeedEntries": total,
        "englishNumberedCoverage": summary,
        "sampleEnglishChapterId": first_chapter_id,
        "sampleOriginalQualityManifest": image_manifest,
        "status": "english-source-candidate" if total else "no-english-feed-entries",
        "metadataOnly": True,
        "imageBytesDownloaded": 0,
        "CBZFilesDownloaded": 0,
        "rightsToArchiveOrRedistributeVerified": False,
        "auditedAtUtc": datetime.now(UTC).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect high-priority user-selected MangaDex title by exact UUID"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("Output file already exists; refusing to overwrite")
    result = audit(MangaDexMetadata(delay=1.7))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "priority": result["priority"],
        "title": result["canonicalSourceTitle"],
        "englishTitleConfirmed": result["englishTitleConfirmed"],
        "englishFeedEntries": result["englishFeedEntries"],
        "numberedChapters": result["englishNumberedCoverage"]["distinctNumberedChapters"],
        "sampleOriginalImagePaths": (
            result["sampleOriginalQualityManifest"] or {}
        ).get("originalPagePaths"),
        "chapterImageBytesDownloaded": 0,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
