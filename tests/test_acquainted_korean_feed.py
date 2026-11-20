"""Offline checks for exact Korean feed and no false language inference."""
from __future__ import annotations

import unittest
from urllib.parse import parse_qs, urlsplit

from scripts.acquainted_korean_feed import MANGA_ID, audit


class FakeClient:
    def __init__(self, korean=(), other=()):
        self.korean = list(korean)
        self.other = list(other)
        self.paths = []

    def request(self, path):
        self.paths.append(path)
        if path == f"/manga/{MANGA_ID}":
            return {"data": {"id": MANGA_ID, "attributes": {"originalLanguage": "ko"}}}
        q = parse_qs(urlsplit(path).query)
        records = self.korean if q.get("translatedLanguage[]") == ["ko"] else self.korean + self.other
        offset = int(q.get("offset", ["0"])[0])
        return {"total": len(records), "data": records[offset:offset+100]}

    def image_manifest(self, chapter_id):
        return {"originalPagePaths": 20, "status": "manifest-only-no-media"}


class KoreanFeedTests(unittest.TestCase):
    def test_original_language_korean_is_not_chapter_evidence(self):
        report = audit(FakeClient())
        self.assertEqual(report["originalLanguage"], "ko")
        self.assertEqual(report["koreanFeedEntries"], 0)
        self.assertEqual(report["unfilteredFeedEntries"], 0)
        self.assertFalse(report["koreanOriginalImageSourceVerified"])
        self.assertEqual(report["mediaBytesDownloaded"], 0)

    def test_available_korean_chapter_has_original_page_manifest(self):
        chapter = {"id": "12345678-1234-4234-8234-123456789012",
                   "attributes": {"chapter": "1", "translatedLanguage": "ko"}}
        report = audit(FakeClient(korean=[chapter]))
        self.assertEqual(report["koreanFeedEntries"], 1)
        self.assertEqual(report["koreanCoverage"]["distinctNumberedChapters"], 1)
        self.assertTrue(report["koreanOriginalImageSourceVerified"])
        self.assertEqual(report["mediaBytesDownloaded"], 0)

    def test_unfiltered_languages_are_not_assumed_korean(self):
        chapter = {"id": "12345678-1234-4234-8234-123456789012",
                   "attributes": {"chapter": "1", "translatedLanguage": "id"}}
        report = audit(FakeClient(other=[chapter]))
        self.assertEqual(report["languagesInVisibleChapterFeed"], {"id": 1})
        self.assertEqual(report["koreanFeedEntries"], 0)


if __name__ == "__main__":
    unittest.main()
