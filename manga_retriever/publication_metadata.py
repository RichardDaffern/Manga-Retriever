"""MangaDex publication metadata enrichment for five pre-identified English manga.

Outputs *review-only* metadata candidates for the Manga Storage Controller.
Never changes chapter IDs, catalogue, private datasets, covers or image bytes.
Cover references are references only, NOT rights-cleared images.

MangaDex acceptable-use rules and credit apply; no user-defined URLs or API IDs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .relife import TITLE_URL as RELIFE_URL
from .selected_sources import SOURCES as SELECTED

API_HOST = "https://api.mangadex.org"
MAX_JSON_BYTES = 1_000_000
UUID = re.compile(r"^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$")
COVER_FILENAME = re.compile(r"^[A-Za-z0-9_-]{1,130}\.(?:png|jpg|jpeg|webp)$")
STATUS = {"completed": "completed", "ongoing": "ongoing", "hiatus": "hiatus"}

# Fixed, previously researched title URLs. No fuzzy title matches or silent
# selection of an alternate edition from the API.
SOURCE_TITLES = {
    "relife": {
        "name": "ReLIFE",
        "aliases": ["ReLIFE"],
        "sourceId": RELIFE_URL.split("/title/")[1].split("/")[0],
    },
    "maid-sama": {
        "name": SELECTED["maid-sama"]["title"],
        "aliases": ["Kaichou wa Maid-sama!", "Maid Sama!", "Maid-sama!"],
        "sourceId": SELECTED["maid-sama"]["id"],
    },
    "last-game": {
        "name": SELECTED["last-game"]["title"],
        "aliases": ["Last Game"],
        "sourceId": SELECTED["last-game"]["id"],
    },
    "love-so-life": {
        "name": SELECTED["love-so-life"]["title"],
        "aliases": ["Love So Life"],
        "sourceId": SELECTED["love-so-life"]["id"],
    },
    "onizuka-sawarida": {
        "name": SELECTED["onizuka-sawarida"]["title"],
        "aliases": ["Onizuka-chan and Sawarida-kun", "Onizuka-chan to Sawarida-kun"],
        "sourceId": SELECTED["onizuka-sawarida"]["id"],
    },
}


class MetadataError(ValueError):
    """A metadata source could not be safely reconciled to a fixed title."""


def _clean(value: object, maximum: int) -> str | None:
    if not isinstance(value, str):
        return None
    text = " ".join(value.split())
    if not text or any(ord(c) < 32 or ord(c) == 127 for c in text):
        return None
    return text[:maximum].strip()


def _key(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKC", value).casefold() if c.isalnum())


def _english(mapping: object, maximum: int) -> str | None:
    if not isinstance(mapping, dict):
        return None
    # English synopsis strictly required; no Japanese fallback to present as English.
    return _clean(mapping.get("en"), maximum)


def _translated_title_candidates(attrs: dict) -> set[str]:
    raw = [*([attrs.get("title")] if attrs.get("title") else []),
           *([attrs.get("altTitles")] if isinstance(attrs.get("altTitles"), list) else [])]
    names = set()
    for entry in raw:
        if isinstance(entry, dict):
            for v in entry.values():
                text = _clean(v, 180)
                if text:
                    names.add(_key(text))
    return names


def _creators(relationships: list[dict]) -> tuple[list[str], list[dict]]:
    names: list[str] = []
    roles: list[dict] = []
    seen: set[str] = set()
    for entry in relationships:
        if entry.get("type") not in ("author", "artist"):
            continue
        attrs = entry.get("attributes") or {}
        name = _clean(attrs.get("name"), 120) if isinstance(attrs, dict) else None
        ident = entry.get("id")
        if not name or not isinstance(ident, str) or not UUID.fullmatch(ident):
            continue
        value = _key(name)
        if value not in seen:
            names.append(name)
            seen.add(value)
        if not any(p["sourceId"] == ident and p["role"] == entry["type"] for p in roles):
            roles.append({"name": name, "role": entry["type"], "sourceId": ident})
    return names[:24], roles[:48]


def normalise(slug: str, payload: object, *, checked_at: str | None = None) -> dict:
    if slug not in SOURCE_TITLES or not isinstance(payload, dict):
        raise MetadataError("Unknown title or metadata response")
    selection = SOURCE_TITLES[slug]
    data = payload.get("data")
    if (payload.get("result") != "ok" or not isinstance(data, dict)
            or data.get("id") != selection["sourceId"] or data.get("type") != "manga"):
        raise MetadataError("MangaDex source identity mismatch")
    attrs = data.get("attributes")
    rels = data.get("relationships")
    if not isinstance(attrs, dict) or not isinstance(rels, list) or len(rels) > 120:
        raise MetadataError("MangaDex attributes or relationships invalid")
    source_titles = _translated_title_candidates(attrs)
    approved_names = {_key(v) for v in selection["aliases"]}
    if not approved_names.intersection(source_titles):
        raise MetadataError("Source edition title mismatch; manual investigation required")
    authors, roles = _creators([item for item in rels if isinstance(item, dict)])
    tags: list[str] = []
    seen_tags: set[str] = set()
    raw_tags = attrs.get("tags")
    if isinstance(raw_tags, list):
        for entry in raw_tags[:80]:
            if not isinstance(entry, dict):
                continue
            properties = entry.get("attributes")
            if not isinstance(properties, dict) or properties.get("group") not in ("genre", "theme"):
                continue
            name = _english(properties.get("name"), 120)
            if name and _key(name) not in seen_tags:
                tags.append(name)
                seen_tags.add(_key(name))
    cover = None
    for item in rels:
        if not isinstance(item, dict) or item.get("type") != "cover_art":
            continue
        props = item.get("attributes")
        filename = props.get("fileName") if isinstance(props, dict) else None
        if isinstance(filename, str) and COVER_FILENAME.fullmatch(filename):
            cover = {
                "sourceUrl": f"https://uploads.mangadex.org/covers/{selection['sourceId']}/{filename}",
                "sourceCoverId": item.get("id"),
                "assetDownloaded": False,
                "rightsClearedForRedistribution": False,
                "status": "reference-only",
            }
        break
    alt_names: list[str] = []
    raw_alt = attrs.get("altTitles")
    if isinstance(raw_alt, list):
        for entry in raw_alt[:60]:
            title = _english(entry, 120)
            if title and _key(title) != _key(selection["name"]) and _key(title) not in {
                    _key(existing) for existing in alt_names}:
                alt_names.append(title)
    source_status = _clean(attrs.get("status"), 24)
    publication_status = STATUS.get(source_status or "", "unknown")
    result = {
        "schemaVersion": 1,
        "mediaKind": "manga",
        "candidateType": "publication-metadata",
        "match": {
            "source": "MangaDex",
            "sourceMangaId": selection["sourceId"],
            "canonicalTitle": selection["name"],
            "aliasesForMatch": selection["aliases"],
            "doesNotContainPrivateMangaId": True,
        },
        "metadata": {
            "title": selection["name"],
            "aliases": alt_names[:24],
            "creators": authors,
            "creatorRoles": roles,
            "tags": tags[:32],
            "synopsis": _english(attrs.get("description"), 2000),
            "publicationStatus": publication_status,
        },
        "coverCandidate": cover,
        "provenance": {
            "sourceUrl": f"https://mangadex.org/title/{selection['sourceId']}",
            "sourceApiUrl": f"{API_HOST}/manga/{selection['sourceId']}",
            "sourceStatus": source_status,
            "retrievedAtUtc": checked_at or datetime.now(UTC).isoformat(),
            "attribution": "Publication metadata from MangaDex; verify original creators and licensors.",
            "sourceEditionMatched": True,
            "operatorReviewRequired": True,
            "replaceManualMetadata": False,
            "coverFileDownloaded": False,
        },
        "missing": [
            field for field, valid in [
                ("creators", bool(authors)), ("synopsis", bool(_english(attrs.get("description"), 2000))),
                ("tags", bool(tags)), ("cover", bool(cover))]
            if not valid
        ],
    }
    return result


def fetch_metadata(slug: str, *, open_url=urlopen) -> dict:
    if slug not in SOURCE_TITLES:
        raise MetadataError("Unknown allowlisted manga slug")
    manga_id = SOURCE_TITLES[slug]["sourceId"]
    if not UUID.fullmatch(manga_id):
        raise MetadataError("Invalid pinned MangaDex source identity")
    params = urlencode([("includes[]", "author"), ("includes[]", "artist"),
                        ("includes[]", "cover_art")])
    request = Request(
        f"{API_HOST}/manga/{manga_id}?{params}",
        headers={"Accept": "application/json",
                 "User-Agent": "Taiyou-Manga-Retriever/0.1 metadata-only (GitHub: RichardDaffern/Manga-Retriever)"},
    )
    try:
        with open_url(request, timeout=20) as response:  # noqa: S310 - fixed HTTPS API URL and redirect destination verified
            if response.status != 200 or response.geturl().split("?")[0] != f"{API_HOST}/manga/{manga_id}":
                raise MetadataError("Unexpected MangaDex endpoint or redirect")
            raw = response.read(MAX_JSON_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise MetadataError("MangaDex metadata temporarily unavailable") from exc
    if len(raw) > MAX_JSON_BYTES:
        raise MetadataError("MangaDex metadata exceeds byte quota")
    try:
        return normalise(slug, json.loads(raw))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise MetadataError("MangaDex returned invalid JSON") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Produce review-only metadata candidate, no cover download")
    parser.add_argument("--slug", choices=sorted(SOURCE_TITLES), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.is_symlink() or args.output.exists():
        print("Refusing to overwrite existing metadata", file=sys.stderr)
        return 1
    try:
        candidate = fetch_metadata(args.slug)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (MetadataError, OSError, ValueError) as exc:
        print(f"Metadata acquisition failed: {exc}", file=sys.stderr)
        return 1
    fields = candidate["metadata"]
    print(json.dumps({
        "slug": args.slug,
        "status": "review-only",
        "creatorCount": len(fields["creators"]),
        "tagCount": len(fields["tags"]),
        "hasEnglishSynopsis": bool(fields["synopsis"]),
        "hasCoverReference": bool(candidate["coverCandidate"]),
        "missing": candidate["missing"],
        "imageFilesDownloaded": 0,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
