"""Offline regression checks for parallel, resumable Windows manga batches."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.local_url_manga_bulk import chunks, run_bulk
from scripts.local_url_manga_download import ChapterPilotError
from scripts.five_manga_catalogue import SOURCES


class MangaBulkTests(unittest.TestCase):
    def test_chunk_boundaries_and_final_batch(self):
        self.assertEqual(chunks(1, 41), [(1, 20), (21, 40), (41, 41)])
        self.assertEqual(chunks(1, 261)[-1], (261, 261))
        with self.assertRaises(ChapterPilotError):
            chunks(0, 30)

    def test_full_requires_english_review_and_rights_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(ChapterPilotError, "Check source terms"):
                run_bulk(["love-hina"], root)
            with self.assertRaisesRegex(ChapterPilotError, "requires review"):
                run_bulk(["love-hina"], root, mode="full",
                         acknowledge_local_rights=True)
            with self.assertRaisesRegex(ChapterPilotError, "unique approved"):
                run_bulk(["love-hina", "love-hina"], root,
                         acknowledge_local_rights=True)
            with self.assertRaisesRegex(ChapterPilotError, "one or two"):
                run_bulk(["love-hina"], root, workers=4,
                         acknowledge_local_rights=True)

    def test_pilot_runs_multiple_series_independently_in_parallel(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            selected = ["nisekoi", "love-hina", "lovely-complex"]
            called = []

            def fake_download(url, selection, output, **kwargs):
                called.append(url)
                output.mkdir()
                return {"status": "verified-image-files-needs-english-review",
                        "verifiedPages": 12, "verifiedArchiveCount": 1,
                        "requiresManualEnglishReview": True}

            with patch("scripts.local_url_manga_bulk.run_pilot", fake_download):
                result = run_bulk(selected, root, mode="pilot",
                                  acknowledge_local_rights=True, workers=2)
            self.assertEqual(result["status"], "verified-local-batches")
            self.assertEqual(sum(t["verifiedPages"] for t in result["titles"]), 36)
            self.assertEqual(set(called), {SOURCES[s]["url"] for s in selected})
            self.assertTrue((root / "manga-bulk-status.json").exists())
            self.assertTrue(all(t["verifiedBatchCount"] == 1 for t in result["titles"]))

    def test_failed_source_does_not_cancel_other_series(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def source_download(url, selection, output, **kwargs):
                if url == SOURCES["nisekoi"]["url"]:
                    raise ChapterPilotError("Source unavailable")
                output.mkdir()
                return {"status": "verified-image-files-needs-english-review",
                        "verifiedPages": 10, "verifiedArchiveCount": 1,
                        "requiresManualEnglishReview": True}

            with patch("scripts.local_url_manga_bulk.run_pilot", source_download):
                r = run_bulk(["nisekoi", "love-hina"], root, mode="pilot",
                             acknowledge_local_rights=True)
            self.assertEqual(r["status"], "partial")
            self.assertEqual(r["titles"][0]["status"], "partial")
            self.assertEqual(r["titles"][1]["status"], "passed")
            self.assertEqual(r["titles"][1]["verifiedPages"], 10)
            saved = json.loads((root / "manga-bulk-status.json").read_text())
            self.assertEqual(saved["status"], "partial")


if __name__ == "__main__":
    unittest.main()
