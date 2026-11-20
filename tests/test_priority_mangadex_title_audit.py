"""Test exact-URL priority audit without network or image downloads."""
from __future__ import annotations

import unittest

from scripts.priority_mangadex_title_audit import MANGA_ID, MANGA_URL, audit


class FakeClient:
    def __init__(self, *, correct=True, chapters=None, title=None):
        self.correct = correct
        self.chapters = chapters if chapters is not None else [
            {"id": "12345678-1234-4234-8234-123456789012",
             "attributes": {"chapter": "1", "translatedLanguage": "en"}},
            {"id": "12345678-1234-4234-8234-123456789013",
             "attributes": {"chapter": "2", "translatedLanguage": "en"}},
        ]
        self.title = title or {"en": "Sample Manga"}
        self.request_paths = []

    def request(self, path):
        self.request_paths.append(path)
        return {"result": "ok", "data": {
            "id": MANGA_ID if self.correct else "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "type": "manga",
            "attributes": {
                "title": self.title, "originalLanguage": "ja", "status": "ongoing"
            },
        }}

    def feed(self, manga_id):
        assert manga_id == MANGA_ID
        return len(self.chapters), self.chapters

    def image_manifest(self, chapter_id):
        assert chapter_id == self.chapters[0]["id"]
        return {"status": "manifest-only-no-artwork-retrieved",
                "originalPagePaths": 21, "dataSaverPagePaths": 21}


class PriorityMangaAuditTests(unittest.TestCase):
    def test_pinned_id_title_and_available_original_page_paths(self):
        report = audit(FakeClient())
        self.assertEqual(report["sourceUrl"], MANGA_URL)
        self.assertEqual(report["englishFeedEntries"], 2)
        self.assertEqual(report["englishNumberedCoverage"]["distinctNumberedChapters"], 2)
        self.assertEqual(report["sampleOriginalQualityManifest"]["originalPagePaths"], 21)
        self.assertTrue(report["englishTitleConfirmed"])
        self.assertEqual(report["imageBytesDownloaded"], 0)
        self.assertFalse(report["rightsToArchiveOrRedistributeVerified"])

    def test_mismatched_source_uuid_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            audit(FakeClient(correct=False))

    def test_no_english_chapters_is_not_marked_as_downloadable(self):
        report = audit(FakeClient(chapters=[]))
        self.assertEqual(report["status"], "no-english-feed-entries")
        self.assertIsNone(report["sampleEnglishChapterId"])

    def test_source_without_english_title_is_explicitly_marked(self):
        report = audit(FakeClient(title={"ja": "日本語タイトル"}))
        self.assertFalse(report["englishTitleConfirmed"])
        self.assertEqual(report["canonicalSourceTitle"], "日本語タイトル")


if __name__ == "__main__":
    unittest.main()
