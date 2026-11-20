"""Offline tests for fail-closed metadata-only source discovery."""
import unittest

from scripts.probe_publication_ids import SEARCH, probe


class FakeClient:
    def __init__(self, items):
        self.items = items
        self.calls = []

    def discover(self, work):
        self.calls.append(work["name"])
        return self.items


class PublicationIdProbeTests(unittest.TestCase):
    def test_six_known_titles_only(self):
        self.assertEqual(len(SEARCH), 6)
        for slug in SEARCH:
            with self.subTest(slug=slug):
                match = {"id": "7a1c6e41-6c2d-401e-90fe-baccb637a63e",
                         "attributes": {"title": {"en": SEARCH[slug]}, "altTitles": []}}
                client = FakeClient((match, [match]))
                result = probe(slug, client)
                self.assertEqual(result["status"], "exact-unambiguous")
                self.assertEqual(result["sourceId"], match["id"])
                self.assertTrue(result["metadataOnly"])
                self.assertFalse(result["rightsToArchiveOrRedistribute"])
                self.assertEqual(client.calls, [SEARCH[slug]])

    def test_ambiguity_never_auto_selects(self):
        vals = [
            {"id": "7a1c6e41-6c2d-401e-90fe-baccb637a63e",
             "attributes": {"title": {"en": "Lovely Complex"}}},
            {"id": "7b273ab1-42cb-4004-8ffd-1c6f580cc107",
             "attributes": {"title": {"en": "Lovely Complex"}}},
        ]
        out = probe("lovely-complex", FakeClient((None, vals)))
        self.assertEqual(out["status"], "ambiguous")
        self.assertIsNone(out["sourceId"])
        self.assertEqual(len(out["candidates"]), 2)

    def test_missing_stays_missing(self):
        out = probe("nisekoi", FakeClient((None, [])))
        self.assertEqual(out["status"], "not-found")
        self.assertIsNone(out["sourceId"])

    def test_unknown_title_rejected(self):
        with self.assertRaises(ValueError):
            probe("random-series", FakeClient((None, [])))


if __name__ == "__main__":
    unittest.main()
