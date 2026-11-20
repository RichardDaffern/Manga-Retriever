"""Offline contract tests for the new ManhuaTop research source."""
from __future__ import annotations

import json
import subprocess
import unittest

from scripts.manhuatop_source_probe import SOURCES, ProbeError, check, evaluate, validate_source


class ManhuaTopProbeTests(unittest.TestCase):
    def test_four_exact_new_series(self):
        self.assertEqual(len(SOURCES), 4)
        for slug in SOURCES:
            self.assertEqual(validate_source(slug), SOURCES[slug])

    def test_reject_unknown_source(self):
        with self.assertRaises(ProbeError):
            validate_source("previously-downloaded-relife")

    def test_reports_access_but_not_language_or_rights(self):
        chapters = [
            {"number": 1.0, "language": "", "locked": False},
            {"number": 2.0, "language": None, "locked": False},
        ]
        result = evaluate("disastrous-necromancer", {"title": "Disastrous Necromancer", "chapters": chapters})
        self.assertEqual(result["visibleChapterEntries"], 2)
        self.assertEqual(result["uniqueNumericChapterLabels"], 2)
        self.assertEqual(result["actualPageImageDownloads"], 0)
        self.assertFalse(result["englishPageTextVerified"])
        self.assertFalse(result["publicMediaDistributionPermitted"])

    def test_wrong_manga_rejected(self):
        with self.assertRaisesRegex(ProbeError, "title mismatch"):
            evaluate("magic-emperor", {"title": "Kainushi wa Akuma", "chapters": [{"number": 1}]})

    def test_list_subprocess_does_not_download(self):
        expected = SOURCES["high-martial-world"]["url"]
        def runner(argv, **kwargs):
            self.assertEqual(argv, ["pinned-client", "list", "--json", expected])
            return subprocess.CompletedProcess(argv, 0, json.dumps({
                "title": SOURCES["high-martial-world"]["title"],
                "chapters": [{"number": 1.0, "language": "en", "locked": False}],
            }).encode(), b"")
        result = check("high-martial-world", "pinned-client", runner=runner)
        self.assertEqual(result["status"], "technical-listing-confirmed-no-rights")
        self.assertFalse(result["rightsToArchiveVerified"])
        self.assertFalse(result["mediaDownloaded"])

    def test_cloud_block_does_not_claim_success(self):
        def runner(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 1, b"", b"blocked")
        result = check("magic-emperor", "pinned-client", runner=runner)
        self.assertEqual(result["status"], "unverified-source-or-client-error")
        self.assertFalse(result["mediaDownloaded"])


if __name__ == "__main__":
    unittest.main()
