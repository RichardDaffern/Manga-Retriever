"""Offline tests of Kainushi chapter metadata comparison, not artwork retrieval."""
from __future__ import annotations

import unittest

from manga_retriever.publication_metadata import SOURCE_TITLES
from scripts.kainushi_gap_audit import (
    ALT_ENGLISH_LISTING_COUNT,
    ALT_INDEXED_LABELS,
    _normalise_label,
    audit,
    compare_labels,
    report_csv,
)


class FakeFeedClient:
    def __init__(self, numbers):
        self.numbers = numbers
        self.requested = []

    def feed(self, source_id):
        self.requested.append(source_id)
        items = [
            {"id": f"row-{i}", "attributes": {"chapter": number}}
            for i, number in enumerate(self.numbers)
        ]
        return len(items), items


class GapAuditTests(unittest.TestCase):
    def test_exact_source_id_and_unverified_count_difference(self):
        client = FakeFeedClient([str(i) for i in range(1, 11)] + ["11.1", "11.2"])
        report = audit(client)
        self.assertEqual(client.requested, [SOURCE_TITLES["kainushi-wa-akuma"]["sourceId"]])
        self.assertEqual(report["englishFeedEntries"], 12)
        self.assertEqual(report["mangaDexCoverage"]["distinctNumberedChapters"], 10)
        self.assertEqual(report["mangaDexCoverage"]["decimalNumberedExtras"], 2)
        self.assertEqual(report["alternativeListing"]["previouslyObservedEnglishEntries"],
                         ALT_ENGLISH_LISTING_COUNT)
        self.assertFalse(report["alternativeListing"]["chapterLabelAlignmentVerified"])
        self.assertFalse(report["alternativeListing"]["downloadRightsVerified"])
        self.assertEqual(report["imageBytesDownloaded"], 0)

    def test_public_index_snapshot_has_56_unique_labels(self):
        self.assertEqual(len(ALT_INDEXED_LABELS), 56)
        self.assertEqual(len(set(ALT_INDEXED_LABELS)), 56)
        self.assertIn("25.5", ALT_INDEXED_LABELS)
        self.assertIn("10.1", ALT_INDEXED_LABELS)
        self.assertNotIn("10", ALT_INDEXED_LABELS)

    def test_exact_label_differences_not_inferred_as_missing_images(self):
        client = FakeFeedClient(["1", "1.1", "3", "10", "11.1", "25.5"])
        result = audit(client)
        comparison = result["alternativeListing"]["exactLabelComparison"]
        self.assertEqual(comparison["mangaDexOnly"], ["10"])
        self.assertEqual(len(comparison["publicIndexOnly"]), 51)
        self.assertEqual(len(comparison["inBothIndexes"]), 5)
        self.assertFalse(comparison["differenceProvesMissingMedia"])
        self.assertFalse(comparison["differenceIndicatesDownloadRights"])
        data = report_csv(result)
        self.assertIn("10,true,false,false", data)
        self.assertIn("25.5,true,true,false", data)

    def test_label_normalisation_is_exact_and_safe(self):
        self.assertEqual(_normalise_label("001.100"), "1.1")
        self.assertEqual(_normalise_label("25"), "25")
        self.assertIsNone(_normalise_label("25a"))
        self.assertIsNone(_normalise_label("-1"))
        self.assertIsNone(_normalise_label("0"))
        self.assertIsNone(_normalise_label("100000"))
        comparison = compare_labels([
            {"id": "one", "attributes": {"chapter": "1"}},
            {"id": "one-repeat", "attributes": {"chapter": "01.00"}},
            {"id": "two", "attributes": {"chapter": None}},
        ])
        self.assertEqual(comparison["duplicatedMangaDexLabels"], ["1"])
        self.assertEqual(comparison["unlabelledMangaDexEntries"], 1)

    def test_incomplete_feed_fails(self):
        client = FakeFeedClient(["1"])
        client.feed = lambda _: (3, [{"id": "one", "attributes": {"chapter": "1"}}])
        with self.assertRaisesRegex(ValueError, "not completely paginated"):
            audit(client)


if __name__ == "__main__":
    unittest.main()
