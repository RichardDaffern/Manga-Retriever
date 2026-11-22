"""Offline regression tests for the exact Nisekoi MangaDex metadata audit."""
from __future__ import annotations

import unittest

from scripts.nisekoi_mangadex_audit import MANGA_ID, MANGA_URL, audit


class FakeClient:
    def __init__(self, *, title="Nisekoi: False Love", correct_id=True,
                 count=229, original_paths=20):
        self.title = title
        self.correct_id = correct_id
        self.count = count
        self.original_paths = original_paths

    def request(self, path):
        return {
            "result": "ok",
            "data": {
                "id": MANGA_ID if self.correct_id else "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "type": "manga",
                "attributes": {
                    "title": {"en": self.title},
                    "originalLanguage": "ja",
                    "status": "completed",
                },
            },
        }

    def feed(self, manga_id):
        assert manga_id == MANGA_ID
        rows = [
            {"id": f"12345678-1234-4234-8234-{n:012d}",
             "attributes": {"chapter": str(n), "translatedLanguage": "en"}}
            for n in range(1, self.count + 1)
        ]
        return len(rows), rows

    def image_manifest(self, chapter_id):
        return {
            "status": "manifest-only-no-artwork-retrieved",
            "originalPagePaths": self.original_paths,
            "dataSaverPagePaths": self.original_paths,
        }


class NisekoiMangaDexAuditTests(unittest.TestCase):
    def test_exact_title_and_complete_numbered_metadata_are_reported(self):
        report = audit(FakeClient())
        self.assertEqual(report["sourceMangaId"], MANGA_ID)
        self.assertEqual(report["sourceUrl"], MANGA_URL)
        self.assertEqual(report["canonicalEnglishTitle"], "Nisekoi: False Love")
        self.assertEqual(report["englishFeedEntries"], 229)
        self.assertTrue(report["numberedMainCoverageComplete"])
        self.assertEqual(report["sampleOriginalQualityManifest"]["originalPagePaths"], 20)
        self.assertEqual(report["chapterImageBytesDownloaded"], 0)
        self.assertFalse(report["rightsToArchiveOrRedistributeVerified"])
        self.assertFalse(report["eligibleForMediaDownload"])

    def test_wrong_uuid_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "exact Nisekoi UUID"):
            audit(FakeClient(correct_id=False))

    def test_wrong_english_title_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "does not exactly identify Nisekoi"):
            audit(FakeClient(title="Nisekoi Doumei"))

    def test_incomplete_feed_is_not_reported_as_complete(self):
        report = audit(FakeClient(count=228))
        self.assertFalse(report["numberedMainCoverageComplete"])
        self.assertEqual(report["numberedCoverage"]["missingPositiveNumbers"], [229])

    def test_zero_original_paths_is_explicitly_cautioned(self):
        report = audit(FakeClient(original_paths=0))
        self.assertEqual(
            report["status"],
            "english-feed-without-hosted-original-page-paths",
        )


if __name__ == "__main__":
    unittest.main()
