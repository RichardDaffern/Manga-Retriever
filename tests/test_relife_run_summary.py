"""Synthetic workflow-run report tests, no manga media."""
from __future__ import annotations

import unittest

from scripts.relife_run_summary import BATCHES, EXPECTED, summarise


class ReLIFERecoveryTests(unittest.TestCase):
    def test_exact_partition(self):
        self.assertEqual(len(EXPECTED), 12)
        self.assertEqual([chapter for start, end in BATCHES for chapter in range(start, end + 1)],
                         list(range(1, 223)))

    def test_all_present(self):
        report = summarise(123, 1, "success", {"artifacts": [
            {"name": name, "expired": False} for name in EXPECTED
        ]})
        self.assertTrue(report["allTwelveAvailable"])
        self.assertEqual(report["availableBatches"], 12)

    def test_missing_and_expired(self):
        report = summarise(123, 2, "failure", {"artifacts": [
            {"name": EXPECTED[0], "expired": True},
            {"name": EXPECTED[1], "expired": False},
            {"name": "untrusted-other", "expired": False},
        ]})
        self.assertEqual(report["availableBatches"], 1)
        self.assertEqual(report["missingOrExpiredArtifactNames"][0], EXPECTED[0])
        self.assertFalse(report["allTwelveAvailable"])

    def test_duplicate_does_not_fake_two_ranges(self):
        report = summarise(123, 1, "success", {"artifacts": [
            {"name": EXPECTED[0], "expired": False},
            {"name": EXPECTED[0], "expired": False},
        ]})
        self.assertEqual(report["availableBatches"], 1)

    def test_invalid_identity_and_shape(self):
        for wrong in (None, {}, {"artifacts": [None]}, {"artifacts": None}):
            with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                summarise(1, 1, "success", wrong)
        with self.assertRaises(ValueError):
            summarise(0, 1, "success", {"artifacts": []})


if __name__ == "__main__":
    unittest.main()
