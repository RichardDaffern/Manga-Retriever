"""One-off, fixed-cover private handover, English manga library, 20 November 2026.

Only downloads the five source-identified existing cover art references. No
chapters, login, scraper or arbitrary URLs. Always validate image bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image

# URLs are copied from verified MangaDex metadata; no user-supplied URL input.
COVERS = {
    "relife": "https://uploads.mangadex.org/covers/6e3553b9-ddb5-4d37-b7a3-99998044774e/1cca330a-bb93-47bb-9173-015a53ec7ce5.png",
    "maid-sama": "https://uploads.mangadex.org/covers/d5e2bd89-e300-4262-a799-fb4f79bdb777/1e3d60d7-7950-4336-a0dc-017ad7a6c378.jpg",
    "last-game": "https://uploads.mangadex.org/covers/32600d3f-a43a-4f90-8a4e-c4e09f35c99b/8dffd748-e73d-4536-8e6e-fcd9ad0d762f.jpg",
    "love-so-life": "https://uploads.mangadex.org/covers/911a12ae-1022-448e-9219-b7b294d7fb3e/1acd3262-ff14-4d63-886b-22f480522f08.jpg",
    "onizuka-sawarida": "https://uploads.mangadex.org/covers/96b87943-6458-4045-a029-d3185d5cea57/6afec02e-2679-49bd-9853-4b92da6f3b93.jpg",
}
MIME = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
EXT = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
MAX_BYTES = 12_000_000


def _image(slug: str, url: str, *, opener=urlopen) -> tuple[bytes, dict]:
    request = Request(  # noqa: S310 - fixed HTTPS MangaDex cover URL
        url, headers={"User-Agent": "Taiyou-Manga-Retriever/1.0 (personal-library; GitHub RichardDaffern/Manga-Retriever)",
                      "Accept": "image/jpeg,image/png,image/webp"},
    )
    with opener(request, timeout=25) as response:  # noqa: S310 - fixed HTTPS cover URL
        if response.status != 200 or response.geturl() != url:
            raise ValueError("Unexpected cover host, redirect or status")
        blob = response.read(MAX_BYTES + 1)
    if not 10_000 <= len(blob) <= MAX_BYTES:
        raise ValueError("Missing or oversized cover image: " + slug)
    with Image.open(io.BytesIO(blob)) as image:
        fmt = image.format
        image.load()
        width, height = image.size
    if fmt not in MIME or width < 240 or height < 240 or width > 6000 or height > 9000:
        raise ValueError("Cover is not a valid full-size image: " + slug)
    if not 0.3 <= width / height <= 1.8:
        raise ValueError("Cover has invalid proportions: " + slug)
    if not url.lower().endswith(EXT[fmt]):
        raise ValueError("Cover format differs from image file extension")
    path = "covers/" + slug + EXT[fmt]
    return blob, {
        "slug": slug, "path": path, "sourceUrl": url,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "bytes": len(blob), "width": width, "height": height,
        "mimeType": MIME[fmt], "rightsClearedForRedistribution": False,
    }


def build(dest: Path, *, opener=urlopen, pause=time.sleep) -> dict:
    if dest.exists() or dest.is_symlink():
        raise ValueError("Existing cover bundle must not be overwritten")
    files = {}
    entries = []
    for i, (slug, url) in enumerate(COVERS.items()):
        if i:
            pause(2)
        image, record = _image(slug, url, opener=opener)
        files[record["path"]] = image
        entries.append(record)
    report = {
        "schemaVersion": 1, "bundleType": "existing-five-cover-images",
        "source": "MangaDex cover image references",
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "covers": entries,
        "count": len(entries),
        "chapterImagesIncluded": False,
        "privateHuggingFaceModified": False,
        "rightsClearedForRedistribution": False,
    }
    files["cover-attachment-manifest.json"] = (
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    ).encode()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, image in files.items():
            archive.writestr(name, image)
    with zipfile.ZipFile(dest) as archive:
        if archive.testzip() is not None or len([p for p in archive.namelist()
                                                if p.startswith("covers/")]) != 5:
            raise ValueError("Incomplete or corrupt 5-cover bundle")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch 5 verified personal library covers")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output)
    print(json.dumps({"coversDownloaded": report["count"], "chaptersDownloaded": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
