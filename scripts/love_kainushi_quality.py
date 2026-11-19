"""Ephemeral image-quality comparison: 2 titles x 2 chapters x 2 image modes.

Reads a tiny, bounded set of pages into memory only, decodes them, and
publishes JSON metrics without retaining or uploading copyrighted image bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image

from scripts.love_kainushi_readiness import labels_from_feed, representative_chapters
from scripts.source_probe_eight import MangaDexMetadata

TITLES = {
    "love-so-life": "911a12ae-1022-448e-9219-b7b294d7fb3e",
    "kainushi-wa-akuma": "2f46b87a-00dd-4cd3-bf47-68126fb05793",
}
MAX_BYTES = 20 * 1024 * 1024
MAX_PIXELS = 40_000_000
MAX_SIDE = 18000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class DoNotRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, _req, _fp, _code, _msg, _headers, _newurl):
        return None


def check_mangadex_host(base: str) -> str:
    """Keep source-controlled @Home base URLs within MangaDex-controlled DNS."""
    if not isinstance(base, str):
        raise ValueError("Invalid chapter image base URL")
    parts = urlsplit(base)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("Unsafe @Home URL")
    if not host.endswith((".mangadex.network", ".mangadex.org")):
        raise ValueError("Untrusted @Home hostname")
    if parts.port not in (None, 443):
        raise ValueError("Unsafe @Home port")
    return base.rstrip("/")


def image_url(base: str, chapter_hash: str, filename: str, quality: str) -> str:
    base = check_mangadex_host(base)
    if quality not in ("data", "data-saver"):
        raise ValueError("Invalid quality mode")
    if not isinstance(chapter_hash, str) or not re.fullmatch(r"[0-9a-f]{32}", chapter_hash):
        raise ValueError("Invalid chapter content hash")
    if not isinstance(filename, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,254}", filename):
        raise ValueError("Unsafe image filename")
    if ".." in filename:
        raise ValueError("Unsafe image filename")
    return f"{base}/{quality}/{chapter_hash}/{filename}"


def image_stats(data: bytes) -> dict:
    """Decode and validate image without retaining original source bytes."""
    if not 1 <= len(data) <= MAX_BYTES:
        raise ValueError("Image missing or too large")
    with Image.open(io.BytesIO(data)) as image:
        width, height = image.size
        if not 1 <= width <= MAX_SIDE or not 1 <= height <= MAX_SIDE or width * height > MAX_PIXELS:
            raise ValueError("Invalid or excessive image dimensions")
        image.load()
        file_format = image.format
        if file_format not in ("PNG", "JPEG", "WEBP"):
            raise ValueError("Unsupported image format")
    return {
        "width": width,
        "height": height,
        "byteSize": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "format": file_format,
        "pixelCount": width * height,
    }


def fetch_single_image(url: str) -> dict:
    opener = urllib.request.build_opener(DoNotRedirect())
    request = urllib.request.Request(url, headers={
        "User-Agent": "Taiyou-Manga-Retriever/0.1 (bounded source-quality test; image not stored)",
        "Accept": "image/png,image/jpeg,image/webp",
    })
    with opener.open(request, timeout=20) as response:
        if response.status != 200:
            raise ValueError("Unexpected image HTTP response")
        mime = response.headers.get("Content-Type", "").split(";")[0].lower()
        if mime not in ("image/png", "image/jpeg", "image/webp"):
            raise ValueError("Invalid image content type")
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Image exceeds download budget")
    return image_stats(data)


def sample_chapter(client: MangaDexMetadata, chapter_label: str, chapter_id: str) -> dict:
    meta = client.request(f"/at-home/server/{chapter_id}?forcePort443=true")
    chapter = meta.get("chapter")
    if not isinstance(chapter, dict):
        raise ValueError("Invalid image manifest")
    original, saver = chapter.get("data"), chapter.get("dataSaver")
    if not isinstance(original, list) or not isinstance(saver, list) or not original or not saver:
        raise ValueError("Chapter has no original/saver page pair")
    if len(original) != len(saver):
        raise ValueError("Original and saver page counts disagree")
    base, chapter_hash = meta.get("baseUrl"), chapter.get("hash")
    output = {"chapterLabel": chapter_label, "pagePosition": 1, "availablePages": len(original),
              "status": "quality-reviewed", "sampledBytesOnly": True}
    # Original and data-saver mode use the same first-page position.
    output["originalUploaded"] = fetch_single_image(image_url(base, chapter_hash, original[0], "data"))
    output["dataSaver"] = fetch_single_image(image_url(base, chapter_hash, saver[0], "data-saver"))
    output["originalAtLeastAsManyPixels"] = (
        output["originalUploaded"]["pixelCount"] >= output["dataSaver"]["pixelCount"]
    )
    return output


def check_title(client: MangaDexMetadata, key: str, manga_id: str) -> dict:
    total, chapters = client.feed(manga_id)
    summary = labels_from_feed(chapters)
    selected = representative_chapters(summary)
    results = []
    if len(selected) > 2:
        selected = [selected[0], selected[-1]]
    for label, chapter_id in selected:
        try:
            record = sample_chapter(client, label, chapter_id)
        except (OSError, ValueError, KeyError, TypeError, urllib.error.HTTPError, urllib.error.URLError) as exc:
            record = {"chapterLabel": label, "status": "sample-failed", "reason": str(exc)[:150]}
        results.append(record)
    return {
        "manga": key,
        "mangaDexId": manga_id,
        "englishFeedEntries": total,
        "sampledChapters": results,
        "successfulChapterSamples": sum(x["status"] == "quality-reviewed" for x in results),
        "pixelEvidence": "Pillow decoded sample pages in volatile GitHub Actions memory, no image bytes persisted",
        "publisherMasterEquivalence": "NOT verified",
        "downloadAndPublicRedistributionRights": "NOT verified",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ephemeral uploaded-original vs data-saver source quality probe")
    parser.add_argument("--output", type=Path, default=Path("reports/source-quality-samples.json"))
    args = parser.parse_args(argv)
    client = MangaDexMetadata(delay=2)
    reports = {}
    for key, manga_id in TITLES.items():
        print(f"Sampling two chapters for {key}, image bytes discarded after decoding", flush=True)
        reports[key] = check_title(client, key, manga_id)
        print(f"Successful samples: {reports[key]['successfulChapterSamples']}/2", flush=True)
    report = {
        "schemaVersion": 1,
        "checkedAtUtc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "imageBytesPersistedOrUploaded": 0,
        "imageQualityModes": ["original-uploaded", "data-saver"],
        "sourceCredits": "MangaDex and its relevant English scanlation groups",
        "rightsNote": "Image access is not a creator or scanlator licence to publish full chapters.",
        "titles": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not any(v["successfulChapterSamples"] for v in reports.values()):
        raise SystemExit("No source-quality samples succeeded; do not claim image resolution verified")
    print("Saved metrics only to", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
