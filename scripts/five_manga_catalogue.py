"""Bounded, metadata-only catalogue audit for five requested manga.

The external client is only invoked with its "list --json" subcommand, which
does not download chapter pages. No source URL is accepted from the command line.
A complete chapter list is not evidence of image fidelity or download rights.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import unicodedata
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

MAX_OUTPUT_BYTES = 2_000_000
MAX_CHAPTERS = 1_500
CLIENT_VERSION = "v25.3.0"
SOURCES = {
    "kimi-no-iru-machi": {
        "title": "Kimi no Iru Machi",
        "aliases": ("Kimi no Iru Machi", "A Town Where You Live"),
        "url": "https://mangakatana.com/manga/kimi-no-iru-machi.2162",
        "expectedMain": 261,
    },
    "love-hina": {
        "title": "Love Hina",
        "aliases": ("Love Hina",),
        "url": "https://mangakatana.com/manga/love-hina.4545",
        "expectedMain": 120,
    },
    "lovely-complex": {
        "title": "Lovely Complex",
        "aliases": ("Lovely Complex", "Love Com", "Love★Com", "Love Complex"),
        "url": "https://mangakatana.com/manga/lovely-complex.6103",
        "expectedMain": 66,
    },
    "mado-kara-madoka-chan": {
        "title": "Mado kara Madoka-chan",
        "aliases": ("Mado kara Madoka-chan", "Madoka from the Window"),
        "url": "https://mangakatana.com/manga/mado-kara-madoka-chan.21642",
        "expectedMain": 74,
    },
    "nisekoi": {
        "title": "Nisekoi",
        "aliases": ("Nisekoi", "Nisekoi: False Love"),
        "url": "https://mangakatana.com/manga/nisekoi.553",
        "expectedMain": 229,
    },
}


class CatalogueError(ValueError):
    """Unexpected or incomplete metadata response."""


def normalise(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKC", value).casefold() if c.isalnum())


def summarise(slug: str, payload: dict) -> dict:
    if slug not in SOURCES or not isinstance(payload, dict):
        raise CatalogueError("Invalid source or listing")
    source = SOURCES[slug]
    title = payload.get("title")
    chapters = payload.get("chapters")
    if not isinstance(title, str) or not isinstance(chapters, list) or len(chapters) > MAX_CHAPTERS:
        raise CatalogueError("Listing title or chapter array invalid / too large")
    if not chapters:
        raise CatalogueError("No chapter metadata returned")
    title_match = normalise(title) in {normalise(a) for a in source["aliases"]}
    expected = source["expectedMain"]
    numbered: set[int] = set()
    duplicates = 0
    decimals: set[str] = set()
    locked = 0
    unnumbered = 0
    chapter_zero = 0
    bad = 0
    languages: set[str] = set()
    for chapter in chapters:
        if not isinstance(chapter, dict):
            bad += 1
            continue
        if chapter.get("locked") is True:
            locked += 1
        if chapter.get("unnumbered") is True:
            unnumbered += 1
            continue
        language = chapter.get("language")
        if isinstance(language, str) and language:
            languages.add(language[:40])
        number = chapter.get("number")
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            bad += 1
            continue
        try:
            value = Decimal(str(number))
        except InvalidOperation:
            bad += 1
            continue
        if not value.is_finite() or not (Decimal("0") <= value < Decimal("10000")):
            bad += 1
            continue
        if value == 0:
            chapter_zero += 1
            continue
        if value == value.to_integral_value():
            if int(value) in numbered:
                duplicates += 1
            numbered.add(int(value))
        else:
            decimals.add(format(value, "f"))
    missing = [n for n in range(1, expected + 1) if n not in numbered]
    complete = title_match and not missing and locked == 0 and bad == 0
    return {
        "sourceTitle": title,
        "titleMatchesExpected": title_match,
        "catalogueStatus": ("complete-numbered-metadata" if complete else
                            "review-title-mismatch" if not title_match else "partial-or-uncertain-metadata"),
        "expectedMainCount": expected,
        "distinctExpectedMain": len([n for n in numbered if 1 <= n <= expected]),
        "missingMainChapters": missing,
        "additionalIntegerLabels": sorted(n for n in numbered if n > expected),
        "decimalLabels": sorted(decimals),
        "listedEntries": len(chapters),
        "duplicateIntegerReleases": duplicates,
        "lockedEntries": locked,
        "unnumberedEntries": unnumbered,
        "chapterZeroExtras": chapter_zero,
        "invalidEntries": bad,
        "languageTags": sorted(languages),
        "englishTranslationVerified": False,
        "imageFidelityVerified": False,
        "downloadOrRedistributionRightsVerified": False,
        "eligibleForAutomatedDownload": False,
        "downloadBlockers": ["English artwork not verified", "Permitted export and public-artefact rights not verified"],
        "imagesDownloaded": 0,
        "archivesCreated": 0,
    }


def list_with_client(slug: str, executable: str, *, run=subprocess.run) -> dict:
    if slug not in SOURCES:
        raise CatalogueError("Unapproved series slug")
    argv = [executable, "list", "--json", SOURCES[slug]["url"]]
    try:
        response = run(argv, capture_output=True, timeout=160, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CatalogueError(f"Metadata client unavailable: {type(exc).__name__}") from exc
    if response.returncode != 0:
        raise CatalogueError(f"Catalogue query exited with code {response.returncode}")
    raw = response.stdout
    if not isinstance(raw, bytes) or len(raw) > MAX_OUTPUT_BYTES:
        raise CatalogueError("Catalogue JSON oversized or invalid")
    try:
        payload = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogueError("Invalid catalogue JSON") from exc
    return summarise(slug, payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only five-manga source listing (no images)")
    parser.add_argument("--slug", required=True, choices=sorted(SOURCES))
    parser.add_argument("--client", required=True, help="Path to pinned manga-downloader CLI")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = {
        "schemaVersion": 1,
        "checkedAtUtc": datetime.now(UTC).isoformat(),
        "series": args.slug,
        "url": SOURCES[args.slug]["url"],
        "clientVersion": CLIENT_VERSION,
        "method": "third-party CLI list --json (chapter metadata only)",
        "mediaDownloaded": False,
        "rightsWarning": "No licence to download, archive or redistribute artwork has been established.",
    }
    exit_code = 0
    try:
        result["catalogue"] = list_with_client(args.slug, args.client)
        summary = result["catalogue"]
        print(json.dumps({
            "series": args.slug,
            "catalogueStatus": summary["catalogueStatus"],
            "foundMain": summary["distinctExpectedMain"],
            "expectedMain": summary["expectedMainCount"],
            "missingMain": summary["missingMainChapters"],
            "extraDecimalCount": len(summary["decimalLabels"]),
            "lockedEntries": summary["lockedEntries"],
            "invalidEntries": summary["invalidEntries"],
            "chapterZeroExtras": summary["chapterZeroExtras"],
            "duplicateIntegerReleases": summary["duplicateIntegerReleases"],
            "listedEntries": summary["listedEntries"],
        }, sort_keys=True), flush=True)
    except CatalogueError as exc:
        result["error"] = str(exc)
        result["catalogueStatus"] = "unverified"
        print(f"{args.slug}: catalogue not verified: {exc}", file=sys.stderr)
        exit_code = 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
