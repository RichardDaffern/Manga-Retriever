"""Read-only, allowlisted ManhuaTop *new title* compatibility audit.

Technical source access is not copyright permission for archiving or
republication. No manga images are fetched or written by this module.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

from scripts.five_manga_catalogue import normalise

SOURCES = {
    "heavenly-demon-normal-life": {
        "title": "The Heavenly Demon Can't Live a Normal Life",
        "aliases": ["The Heavenly Demon Can't Live a Normal Life", "The Heavenly Demon Cannot Live a Normal Life"],
        "url": "https://manhuatop.org/manhua/the-heavenly-demon-cant-live-a-normal-life-mh/",
    },
    "disastrous-necromancer": {
        "title": "Disastrous Necromancer",
        "aliases": ["Disastrous Necromancer", "Catastrophic Necromancer"],
        "url": "https://manhuatop.org/manhua/disastrous-necromancer-top/",
    },
    "high-martial-world": {
        "title": "High-Martial World: One Hand to Overwhelm Three Thousand Emperors!",
        "aliases": [
            "High-Martial World: One Hand to Overwhelm Three Thousand Emperors!",
            "High Martial World: One Hand to Overwhelm Three Thousand Emperors!",
            "High Martial World: Single-Handedly Sweeping Through Three Thousand Emperors",
        ],
        "url": "https://manhuatop.org/manhua/high-martial-world-one-hand-to-overwhelm-three-thousand-emperors/",
    },
    "magic-emperor": {
        "title": "Magic Emperor",
        "aliases": ["Magic Emperor", "Demonic Emperor", "The Devil Butler"],
        "url": "https://manhuatop.org/manhua/magic-emperor/",
    },
}
MAX_BYTES = 3_000_000
MAX_CHAPTERS = 6000


class ProbeError(ValueError):
    """ManhuaTop chapter listing is unavailable or unverified."""


def validate_source(slug: str) -> dict:
    if slug not in SOURCES:
        raise ProbeError("Unlisted source key")
    source = SOURCES[slug]
    u = urlsplit(source["url"])
    if (u.scheme != "https" or u.netloc != "manhuatop.org"
            or not u.path.startswith("/manhua/") or u.query or u.fragment
            or u.username or u.password or u.port is not None):
        raise ProbeError("Invalid reviewed source URL")
    return source


def evaluate(slug: str, payload: dict) -> dict:
    source = validate_source(slug)
    if not isinstance(payload, dict):
        raise ProbeError("Unexpected catalogue response")
    title = payload.get("title")
    chapters = payload.get("chapters")
    if not isinstance(title, str) or not isinstance(chapters, list):
        raise ProbeError("No valid chapter listing from upstream")
    if not chapters or len(chapters) > MAX_CHAPTERS:
        raise ProbeError("Empty or excessive chapter catalogue")
    if normalise(title) not in {normalise(a) for a in source["aliases"]}:
        raise ProbeError("Source title mismatch; abort rather than pick wrong manga")
    numbers: set[str] = set()
    languages: set[str] = set()
    locked = 0
    malformed = 0
    for c in chapters:
        if not isinstance(c, dict):
            malformed += 1
            continue
        n = c.get("number")
        if type(n) in (int, float) and 0 <= n <= 9999:
            numbers.add(str(n))
        else:
            malformed += 1
        lang = c.get("language")
        if isinstance(lang, str) and lang:
            languages.add(lang.casefold())
        if c.get("locked") is True:
            locked += 1
    if malformed == len(chapters):
        raise ProbeError("Chapter numbering unusable")
    return {
        "sourceTitle": title,
        "visibleChapterEntries": len(chapters),
        "uniqueNumericChapterLabels": len(numbers),
        "languageTags": sorted(languages),
        "lockedEntries": locked,
        "unrecognisedChapterEntries": malformed,
        "englishPageTextVerified": False,
        "actualPageImageDownloads": 0,
        "cbzCreated": 0,
        "rightsToDownloadOrExportVerified": False,
        "publicMediaDistributionPermitted": False,
        "technicalStatus": "chapter-listing-readable",
    }


def check(slug: str, executable: str, *, runner=subprocess.run) -> dict:
    source = validate_source(slug)
    result = {
        "schemaVersion": 1,
        "title": source["title"],
        "slug": slug,
        "sourceUrl": source["url"],
        "provider": "ManhuaTop",
        "upstreamClient": "elboletaire/manga-downloader v25.3.0",
        "checkedAtUtc": datetime.now(UTC).isoformat(),
        "mediaDownloaded": False,
        "rightsToArchiveVerified": False,
    }
    try:
        response = runner(
            [executable, "list", "--json", source["url"]],
            capture_output=True, timeout=180, check=False,
        )
        if response.returncode != 0:
            raise ProbeError(f"Site listing unavailable, client exit code {response.returncode}")
        data = response.stdout
        if not isinstance(data, bytes) or len(data) > MAX_BYTES:
            raise ProbeError("Invalid or oversized response")
        result["catalogue"] = evaluate(slug, json.loads(data))
        result["status"] = "technical-listing-confirmed-no-rights"
    except (ProbeError, OSError, subprocess.TimeoutExpired, ValueError, TypeError) as exc:
        result["status"] = "unverified-source-or-client-error"
        result["error"] = f"{type(exc).__name__}: {exc}"[:240]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Check four new ManhuaTop titles without downloading media")
    parser.add_argument("--slug", choices=sorted(SOURCES), required=True)
    parser.add_argument("--client", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("Existing report is never overwritten")
    record = check(args.slug, args.client)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False))
    return 0 if record["status"] == "technical-listing-confirmed-no-rights" else 1


if __name__ == "__main__":
    raise SystemExit(main())
