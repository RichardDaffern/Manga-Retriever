"""Offline tests of manga chapter sequencing and manifest fidelity boundaries."""
from __future__ import annotations

import unittest

from scripts.love_kainushi_readiness import (
    TITLES,
    KAINUSHI_EXTERNAL_LABELS,
    external_label_difference,
    evaluate,
    labels_from_feed,
    representative_chapters,
    summarise_manifest,
)


def record(label, *, uid=None, volume="1", external=None):
    return {"id": uid or "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "attributes": {"chapter": label, "volume": volume, "externalUrl": external}}


class MangaReadinessTests(unittest.TestCase):
    def test_both_exact_targets(self):
        self.assertEqual(set(TITLES), {"love-so-life", "kainushi-wa-akuma"})
        self.assertEqual(TITLES["love-so-life"]["expectedMain"], 106)

    def test_fractional_labels_preserved_not_miscounted(self):
        rows = [record(x) for x in ["1", "1.1", "1.2", "2", "2.1", "4", "4.5", "1.1"]]
        summary = labels_from_feed(rows)
        self.assertEqual(summary["integerChapterCount"], 3)
        self.assertEqual(summary["missingIntegerLabelsToMax"], ["3"])
        self.assertEqual(summary["decimalLabels"], ["1.1", "1.2", "2.1", "4.5"])
        self.assertEqual(summary["duplicateReleaseLabels"], {"1.1": 2})

    def test_sample_beginning_middle_end(self):
        rows = [record(str(i), uid=f"{i:08x}-aaaa-aaaa-aaaa-aaaaaaaaaaaa") for i in range(1, 7)]
        found = representative_chapters(labels_from_feed(rows))
        self.assertEqual([name for name, _ in found], ["1", "3", "6"])

    def test_hosted_preferred_over_external(self):
        rows = [record("1", uid="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", external="https://reader.test"),
                record("1", uid="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")]
        self.assertEqual(representative_chapters(labels_from_feed(rows))[0][1],
                         "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

    def test_manifest_does_not_claim_image_resolution(self):
        result = summarise_manifest({"chapter": {"data": ["abc.png", "def.jpg"],
                                                 "dataSaver": ["abc.jpg", "def.jpg"]}})
        self.assertEqual(result["originalPaths"], 2)
        self.assertEqual(result["originalExtensions"], {".jpg": 1, ".png": 1})
        self.assertTrue(result["matchingPageCounts"])
        self.assertIn("cannot establish", result["qualityLimit"])

    def test_manifest_fail_closed(self):
        for data in ({}, {"chapter": {}}, {"chapter": {"data": "no", "dataSaver": []}}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                summarise_manifest(data)

    def test_love_expected_coverage_and_no_rights_claim(self):
        class Client:
            def feed(self, manga_id):
                self.called = manga_id
                return 3, [record("1"), record("2"), record("3")]
            def request(self, _path):
                return {"chapter": {"data": ["one.png"], "dataSaver": ["one.jpg"]}}
        client = Client()
        result = evaluate("love-so-life", client)
        self.assertEqual(result["englishFeedEntries"], 3)
        self.assertEqual(len(result["missingExpectedMainNumbers"]), 103)
        self.assertFalse(result["publicMediaArtefactAuthorised"])
        self.assertEqual(len(result["sampleImageManifests"]), 3)

    def test_kainushi_56_external_labels_11_missing_in_manifest(self):
        self.assertEqual(len(KAINUSHI_EXTERNAL_LABELS), 56)
        differences = external_label_difference(["1", "1.2", "2"], KAINUSHI_EXTERNAL_LABELS)
        self.assertIn("1.1", differences["labelsMissingFromMangaDex"])
        self.assertIn("25.5", differences["labelsMissingFromMangaDex"])
        self.assertEqual(differences["labelsAbsentFromExternalIndex"], [])

    def test_kainushi_exact_match_must_be_unambiguous(self):
        class Client:
            def discover(self, _work):
                return None, [{"id": "a"}, {"id": "b"}]
        result = evaluate("kainushi-wa-akuma", Client())
        self.assertEqual(result["status"], "title-ambiguous")
        self.assertFalse(result["downloadAuthorised"])


if __name__ == "__main__":
    unittest.main()
