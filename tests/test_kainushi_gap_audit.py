"""Offline tests of Kainushi chapter metadata comparison, not artwork retrieval."""
from __future__ import annotations

import unittest

from manga_retriever.publication_metadata import SOURCE_TITLES
from scripts.kainushi_gap_audit import ALT_ENGLISH_LISTING_COUNT, audit


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

    def test_incomplete_feed_fails(self):
        client = FakeFeedClient(["1"])
        client.feed = lambda _: (3, [{"id": "one", "attributes": {"chapter": "1"}}])
        with self.assertRaisesRegex(ValueError, "not completely paginated"):
            audit(client)


if __name__ == "__main__":
    unittest.main()
