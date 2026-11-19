"""Offline regression tests of the eight-title source identification."""
from __future__ import annotations
import unittest
from scripts.source_probe_eight import WORKS, check_work, normalise, select_exact, summarise

class SourceProbeEightTests(unittest.TestCase):
    def test_normalise_punctuation(self):
        self.assertEqual(normalise("Onizuka-chan & Sawarida-kun"), "onizukachansawaridakun")
        self.assertEqual(normalise("Lovely Complex"), "lovelycomplex")

    def test_all_exact_eight_titles_present(self):
        self.assertEqual(len(WORKS), 8)
        self.assertEqual(len({w["name"] for w in WORKS}), 8)

    def test_exact_alias_not_random_partial_title(self):
        candidates = [
            {"id": "a" * 8 + "-aaaa-aaaa-aaaa-" + "a" * 12,
             "attributes": {"title": {"en": "Nisekoi: False Love"}, "altTitles": []}},
            {"id": "b" * 8 + "-bbbb-bbbb-bbbb-" + "b" * 12,
             "attributes": {"title": {"en": "Nisekoi Doumei"}, "altTitles": []}},
        ]
        item, matches = select_exact(candidates, ["Nisekoi", "Nisekoi: False Love"])
        self.assertEqual(item["id"], candidates[0]["id"])
        self.assertEqual(len(matches), 1)

    def test_ambiguous_title_fails_closed(self):
        ids = ["a" * 8, "b" * 8]
        items = [{"id": lead + "-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                  "attributes": {"title": {"en": "Last Game"}}} for lead in ids]
        selected, matches = select_exact(items, ["Last Game"])
        self.assertIsNone(selected)
        self.assertEqual(len(matches), 2)

    def test_chapter_summary_deduplicates_and_detects_gaps(self):
        data = [{"id": "x", "attributes": {"chapter": v}} for v in ["1","1","2","4","4.5",None]]
        record = summarise(data)
        self.assertEqual(record["distinctNumberedChapters"], 3)
        self.assertEqual(record["missingPositiveNumbers"], [3])
        self.assertEqual(record["decimalNumberedExtras"], 1)
        self.assertEqual(record["unnumberedEntries"], 1)

    def test_no_match_stays_not_found_without_feeds(self):
        class FakeClient:
            def discover(self, work):
                return None, []
            def feed(self, _):
                self.fail("must not call feed")
        record = check_work({"name": "None", "aliases": [], "queries": []}, FakeClient())
        self.assertEqual(record["status"], "not-found")
        self.assertIsNone(record["imageManifest"])

if __name__ == "__main__":
    unittest.main()
