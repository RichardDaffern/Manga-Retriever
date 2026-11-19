"""Read-only MangaDex source discovery for eight user-requested manga.

This script retrieves title/chapter metadata and a single chapter's public
image *manifest*. It never retrieves image bytes, archives, user files or keys.
Metadata access does not imply a licence to retain or redistribute images.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api.mangadex.org"
UUID = re.compile(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}")
MAX_JSON_BYTES = 1_000_000
MAX_ENTRIES = 800

WORKS = [
    {"name": "Kainushi wa Akuma", "queries": ["Kainushi wa Akuma"],
     "aliases": ["Kainushi wa Akuma"]},
    {"name": "Kimi no Iru Machi", "queries": ["Kimi no Iru Machi", "A Town Where You Live"],
     "aliases": ["Kimi no Iru Machi", "A Town Where You Live"]},
    {"name": "Last Game", "queries": ["Last Game"],
     "aliases": ["Last Game"]},
    {"name": "Love Hina", "queries": ["Love Hina"],
     "aliases": ["Love Hina"]},
    {"name": "Lovely Complex", "queries": ["Lovely Complex", "Love Com"],
     "aliases": ["Lovely Complex", "Love Com", "LoveCom"]},
    {"name": "Mado kara Madoka-chan", "queries": ["Mado kara Madoka-chan"],
     "aliases": ["Mado kara Madoka-chan", "Madoka from the Window"]},
    {"name": "Nisekoi", "queries": ["Nisekoi"],
     "aliases": ["Nisekoi", "Nisekoi: False Love"]},
    {"name": "Onizuka-chan and Sawarida-kun",
     "queries": ["Onizuka-chan to Sawarida-kun", "Onizuka-chan and Sawarida-kun"],
     "aliases": ["Onizuka-chan to Sawarida-kun",
                 "Onizuka-chan and Sawarida-kun", "Ms. Onizuka & Mr. Sawarida"]},
]


def normalise(value: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKC", value).casefold() if ch.isalnum())


def titles_for(candidate: dict) -> list[str]:
    attributes = candidate.get("attributes", {})
    values = list((attributes.get("title") or {}).values())
    for alt in attributes.get("altTitles") or []:
        if isinstance(alt, dict):
            values.extend(v for v in alt.values() if isinstance(v, str))
    return [v for v in values if isinstance(v, str)]


def select_exact(candidates: list[dict], aliases: list[str]) -> tuple[dict | None, list[dict]]:
    """Never silently choose a non-exact search result or an ambiguous title."""
    accepted = {normalise(v) for v in aliases}
    matching = []
    for candidate in candidates:
        if not isinstance(candidate, dict) or not UUID.fullmatch(str(candidate.get("id", ""))):
            continue
        if any(normalise(v) in accepted for v in titles_for(candidate)):
            matching.append(candidate)
    unique = {v["id"]: v for v in matching}
    matching = list(unique.values())
    if len(matching) == 1:
        return matching[0], matching
    return None, matching


def summarise(chapters: list[dict]) -> dict:
    numbers: set[int] = set()
    decimals: set[str] = set()
    unnumbered = 0
    first: dict | None = None
    for item in chapters:
        if not isinstance(item, dict):
            unnumbered += 1
            continue
        value = item.get("attributes", {}).get("chapter")
        if isinstance(value, str) and re.fullmatch(r"[0-9]+", value):
            num = int(value)
            if num > 0:
                numbers.add(num)
                if first is None or num < first["number"]:
                    first = {"number": num, "id": item.get("id")}
        elif isinstance(value, str) and re.fullmatch(r"[0-9]+\.[0-9]+", value):
            decimals.add(value)
        else:
            unnumbered += 1
    highest = max(numbers) if numbers else None
    return {
        "distinctNumberedChapters": len(numbers),
        "firstNumberedChapter": min(numbers) if numbers else None,
        "highestNumberedChapter": highest,
        "missingPositiveNumbers": [x for x in range(1, min(1000, highest or 0) + 1) if x not in numbers],
        "decimalNumberedExtras": len(decimals),
        "unnumberedEntries": unnumbered,
        "firstChapterId": first["id"] if first else None,
    }


class MangaDexMetadata:
    def __init__(self, *, delay: float = 1.7) -> None:
        self.delay = delay

    def request(self, path: str) -> dict:
        if not path.startswith(("/manga?", "/manga/", "/at-home/server/")):
            raise ValueError("Unexpected metadata endpoint")
        url = BASE + path
        headers = {
            "User-Agent": "Taiyou-Manga-Retriever/0.1 (metadata-only; contact via GitHub)",
            "Accept": "application/json",
        }
        for attempt in range(3):
            time.sleep(self.delay)
            try:
                with urlopen(Request(url, headers=headers), timeout=20) as response:
                    if response.status != 200:
                        raise ValueError("Unexpected MangaDex API status")
                    raw = response.read(MAX_JSON_BYTES + 1)
                    if len(raw) > MAX_JSON_BYTES:
                        raise ValueError("MangaDex metadata response exceeds quota")
                    result = json.loads(raw)
                    if not isinstance(result, dict):
                        raise ValueError("Invalid MangaDex JSON object")
                    return result
            except HTTPError as exc:
                if exc.code not in {408, 429, 500, 502, 503, 504} or attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
            except URLError:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
        raise ValueError("Metadata request failed")

    def discover(self, work: dict) -> tuple[dict | None, list[dict]]:
        candidates: dict[str, dict] = {}
        for query in work["queries"]:
            response = self.request("/manga?" + urlencode({"title": query, "limit": 30}))
            for entry in response.get("data", []):
                if isinstance(entry, dict) and UUID.fullmatch(str(entry.get("id", ""))):
                    candidates[entry["id"]] = entry
            selected, matches = select_exact(list(candidates.values()), work["aliases"])
            if selected is not None:
                return selected, matches
        return select_exact(list(candidates.values()), work["aliases"])

    def feed(self, manga_id: str) -> tuple[int, list[dict]]:
        if not UUID.fullmatch(manga_id):
            raise ValueError("Untrusted title identifier")
        chapters: list[dict] = []
        total = None
        for offset in range(0, MAX_ENTRIES, 100):
            q = urlencode({"limit": 100, "offset": offset, "translatedLanguage[]": "en"})
            response = self.request(f"/manga/{manga_id}/feed?{q}")
            entries = response.get("data")
            if not isinstance(entries, list):
                raise ValueError("Invalid chapter feed")
            if total is None:
                total = response.get("total")
                if type(total) is not int or total < 0 or total > MAX_ENTRIES:
                    raise ValueError("Unbounded chapter feed; manual inspection needed")
            chapters.extend(entries)
            if len(chapters) >= total:
                break
        if total is None or len(chapters) != total:
            raise ValueError("Incomplete paginated chapter feed")
        return total, chapters

    def image_manifest(self, chapter_id: str) -> dict:
        if not isinstance(chapter_id, str) or not UUID.fullmatch(chapter_id):
            return {"status": "unavailable", "originalPagePaths": None, "dataSaverPagePaths": None}
        payload = self.request("/at-home/server/" + chapter_id)
        original = payload.get("chapter", {}).get("data")
        saver = payload.get("chapter", {}).get("dataSaver")
        if not isinstance(original, list) or not isinstance(saver, list):
            raise ValueError("Incomplete chapter image manifest")
        return {"status": "manifest-only-no-artwork-retrieved",
                "originalPagePaths": len(original), "dataSaverPagePaths": len(saver)}


def check_work(work: dict, client: MangaDexMetadata) -> dict:
    result = {
        "name": work["name"],
        "status": "not-found",
        "source": "MangaDex",
        "sourceUrl": None,
        "englishFeedEntries": None,
        "numberedCoverage": None,
        "imageManifest": None,
        "candidateTitles": [],
        "error": None,
    }
    try:
        selected, matches = client.discover(work)
        result["candidateTitles"] = [
            {"id": x["id"], "title": next(iter(titles_for(x)), "Untitled")} for x in matches[:5]
        ]
        if selected is None:
            result["status"] = "ambiguous" if matches else "not-found"
            # Lovely Complex has a conventional and a separately listed digital
            # coloured edition. Inspect both, but never choose one silently.
            if matches and work["name"] == "Lovely Complex":
                result["editionAlternatives"] = []
                for candidate in matches[:3]:
                    record = {"mangaDexId": candidate["id"],
                              "title": next(iter(titles_for(candidate)), "Untitled")}
                    try:
                        total, chapters = client.feed(candidate["id"])
                        record["englishFeedEntries"] = total
                        summary = summarise(chapters)
                        chapter_id = summary.pop("firstChapterId")
                        record["numberedCoverage"] = summary
                        if chapter_id is not None:
                            record["sampleImageManifest"] = client.image_manifest(chapter_id)
                    except (OSError, ValueError, KeyError, TypeError) as exc:
                        record["error"] = str(exc)[:160]
                    result["editionAlternatives"].append(record)
            return result
        manga_id = selected["id"]
        result["sourceUrl"] = f"https://mangadex.org/title/{manga_id}"
        result["mangaDexId"] = manga_id
        total, chapters = client.feed(manga_id)
        result["englishFeedEntries"] = total
        coverage = summarise(chapters)
        chapter_id = coverage.pop("firstChapterId")
        result["numberedCoverage"] = coverage
        result["status"] = "english-metadata-present" if total else "no-english-entries"
        if chapter_id is not None:
            try:
                result["imageManifest"] = client.image_manifest(chapter_id)
                if result["imageManifest"].get("originalPagePaths") == 0:
                    result["sourceCaution"] = (
                        "The sampled first English chapter exposes no MangaDex-hosted "
                        "original image pages; it may be an external-reader link."
                    )
            except (OSError, ValueError, TypeError, KeyError) as exc:
                result["imageManifest"] = {"status": "unavailable", "error": str(exc)[:160]}
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result["status"] = "source-check-failed"
        result["error"] = str(exc)[:200]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Eight manga titles: public metadata only, no artwork")
    parser.add_argument("--output", type=Path, default=Path("reports/manga-source-audit-eight.json"))
    args = parser.parse_args()
    client = MangaDexMetadata()
    results = []
    for work in WORKS:
        print(f"Checking public catalogue for {work['name']}...", flush=True)
        current = check_work(work, client)
        results.append(current)
        print(f"  {current['status']} / English entries: {current['englishFeedEntries']}", flush=True)
    report = {
        "schemaVersion": 1,
        "checkedAtUtc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": "Public MangaDex title search, English chapter feed, and image-path manifest only",
        "imagesDownloaded": 0,
        "cbzCreated": 0,
        "rightsWarning": "Metadata is not permission to archive images or publish artwork in GitHub Actions.",
        "titles": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"checked": len(results), "withEnglish": sum(x["status"] == "english-metadata-present" for x in results),
                      "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
