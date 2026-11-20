"""Discover *candidate* MangaDex IDs for six remaining titles, metadata only.

This is a read-only, exact-title, fail-closed research probe. Do not import an
unconfirmed or ambiguous source ID into any private manga catalogue.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.source_probe_eight import MangaDexMetadata, WORKS, titles_for

SEARCH = {
    "kainushi-wa-akuma": "Kainushi wa Akuma",
    "kimi-no-iru-machi": "Kimi no Iru Machi",
    "love-hina": "Love Hina",
    "lovely-complex": "Lovely Complex",
    "mado-kara-madoka-chan": "Mado kara Madoka-chan",
    "nisekoi": "Nisekoi",
}


def probe(slug: str, client: MangaDexMetadata) -> dict:
    if slug not in SEARCH:
        raise ValueError("Unapproved manga discovery title")
    work = next(item for item in WORKS if item["name"] == SEARCH[slug])
    selected, matches = client.discover(work)
    return {
        "schemaVersion": 1,
        "title": work["name"],
        "slug": slug,
        "status": "exact-unambiguous" if selected else (
            "ambiguous" if matches else "not-found"
        ),
        "sourceId": selected["id"] if selected else None,
        "candidates": [
            {"id": item["id"], "titles": titles_for(item)[:12]} for item in matches[:12]
        ],
        "retrievedAtUtc": datetime.now(UTC).isoformat(),
        "metadataOnly": True,
        "rightsToArchiveOrRedistribute": False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Find exact MangaDex metadata IDs, never manga images")
    p.add_argument("--slug", choices=sorted(SEARCH), required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        p.error("Output already exists")
    result = probe(args.slug, MangaDexMetadata(delay=1.7))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"title": result["title"], "status": result["status"],
                      "sourceId": result["sourceId"],
                      "matches": len(result["candidates"]), "imageBytesDownloaded": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
