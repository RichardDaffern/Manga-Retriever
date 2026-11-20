"""Offline tests for completeness, no-media and integrity of 11-title metadata bundle."""
from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from manga_retriever.publication_metadata import MetadataError, SOURCE_TITLES, normalise
from scripts.package_publication_metadata import make_bundle
from tests.test_publication_metadata import payload


class PublicationMetadataBundleTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.input = self.root / "candidates"
        self.input.mkdir()
        self.output = self.root / "metadata-review.zip"

    def write(self, slug):
        (self.input / (slug + ".json")).write_text(
            json.dumps(normalise(slug, payload(slug))), encoding="utf-8"
        )

    def test_all_eleven_candidates_are_in_one_review_only_zip(self):
        for slug in SOURCE_TITLES:
            self.write(slug)
        report = make_bundle(self.input, self.output)
        self.assertEqual(report["records"], 11)
        self.assertTrue(report["complete"])
        self.assertFalse(report["privateCatalogueModified"])
        self.assertEqual(report["coversDownloaded"], 0)
        self.assertEqual(report["imageBytesDownloaded"], 0)
        with zipfile.ZipFile(self.output) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len(archive.namelist()), 13)
            self.assertTrue(set(archive.namelist()).issuperset(
                {f"candidates/{slug}.json" for slug in SOURCE_TITLES}
            ))
            rows = list(csv.DictReader(io.StringIO(archive.read("metadata-review.csv").decode())))
            self.assertEqual(len(rows), 11)
            self.assertTrue(all(row["coverDownloaded"] == "False" for row in rows))
            self.assertTrue(all(row["requiresReview"] == "True" for row in rows))
            manifest = json.loads(archive.read("manifest.json"))
            self.assertEqual(len(manifest["files"]), 12)
            self.assertEqual(manifest["bundleType"], "publication-metadata-review")

    def test_partial_requires_explicit_allowance(self):
        self.write("relife")
        with self.assertRaisesRegex(MetadataError, "Incomplete"):
            make_bundle(self.input, self.output)
        self.assertFalse(self.output.exists())
        report = make_bundle(self.input, self.output, require_all=False)
        self.assertEqual(report["records"], 1)
        self.assertIn("nisekoi", report["missingSlugs"])

    def test_unsafe_or_mismatched_candidate_rejected(self):
        self.write("relife")
        src = self.input / "relife.json"
        record = json.loads(src.read_text())
        record["match"]["sourceMangaId"] = SOURCE_TITLES["nisekoi"]["sourceId"]
        src.write_text(json.dumps(record))
        with self.assertRaises(MetadataError):
            make_bundle(self.input, self.output, require_all=False)
        self.assertFalse(self.output.exists())

    def test_extra_unexpected_file_and_overwrite_protection(self):
        self.write("relife")
        (self.input / "unrelated.txt").write_text("do not package")
        with self.assertRaises(MetadataError):
            make_bundle(self.input, self.output, require_all=False)
        (self.input / "unrelated.txt").unlink()
        self.output.write_text("keep")
        with self.assertRaises(MetadataError):
            make_bundle(self.input, self.output, require_all=False)
        self.assertEqual(self.output.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
