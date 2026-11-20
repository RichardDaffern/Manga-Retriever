"""Offline integration tests for English original-image ZIP and fixed-layout EPUB."""
from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image

from manga_retriever.alternative_formats import (
    EPUB_MIME,
    _verify_outputs,
    package_verified_export,
    verified_english_pages,
)
from manga_retriever.importer import ImportFailure, verify_export
from manga_retriever.peppercarrot import LICENCE_URL, SOURCE_PAGE, download_episode_26

PAGE_ROOT = (
    "https://www.peppercarrot.com/0_sources/ep26_Books-Are-Great/hi-res/"
    "en_Pepper-and-Carrot_by-David-Revoy_E26P"
)


def sample_jpeg(index: int) -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (30 + index, 32 + index), (index * 26, 45, 23)).save(out, format="JPEG")
    return out.getvalue()


def official_page() -> bytes:
    links = "".join(f'<a href="{PAGE_ROOT}{n:02d}.jpg">Page {n}</a>' for n in range(1, 7))
    return (
        f'<h1>Episode 26: Books Are Great</h1><span>David Revoy</span>'
        f'<a href="{LICENCE_URL}">CC BY 4.0</a>{links}'
    ).encode()


class AlternativeFormatsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.export = self.base / "licensed-export"
        self.output = self.base / "formats"
        self.original = {n: sample_jpeg(n) for n in range(1, 7)}

        def fetch(url: str, _limit: int) -> bytes:
            if url == SOURCE_PAGE:
                return official_page()
            if url.startswith(PAGE_ROOT) and url.endswith(".jpg"):
                return self.original[int(url[-6:-4])]
            raise AssertionError("Network request for unexpected URL")

        self.assertEqual(
            download_episode_26(self.export, self.base / "ids.json", fetch=fetch, sleep=lambda _: None),
            {"series": 1, "chapters": 1, "pages": 6},
        )

    def test_real_original_bytes_preserved_across_zip_and_epub(self):
        report = package_verified_export(self.export, self.output)
        self.assertEqual(report["status"], "verified-media")
        self.assertEqual(report["language"], "en")
        self.assertEqual(report["pages"], 6)
        self.assertEqual(len(report["formats"]), 2)
        self.assertEqual(verify_export(self.export)["pages"], 6)
        with zipfile.ZipFile(self.output / "english-original-images.zip") as imgzip:
            self.assertIsNone(imgzip.testzip())
            for n in range(1, 7):
                self.assertEqual(imgzip.read(f"pages/{n:04d}.jpg"), self.original[n])
            self.assertIn("David Revoy", imgzip.read("ATTRIBUTION.txt").decode())
        with zipfile.ZipFile(self.output / "english-fixed-layout.epub") as epub:
            self.assertIsNone(epub.testzip())
            self.assertEqual(epub.namelist()[0], "mimetype")
            self.assertEqual(epub.read("mimetype"), EPUB_MIME)
            self.assertEqual(epub.getinfo("mimetype").compress_type, zipfile.ZIP_STORED)
            for name in epub.namelist():
                if name.endswith((".xml", ".opf", ".xhtml")):
                    ElementTree.fromstring(epub.read(name))  # noqa: S314 - locally generated XML only
            for n in range(1, 7):
                self.assertEqual(epub.read(f"EPUB/images/p{n:04d}.jpg"), self.original[n])
            self.assertIn("Creative Commons", epub.read("EPUB/ATTRIBUTION.txt").decode())
        self.assertTrue((self.output / "verification.json").is_file())
        for item in report["formats"]:
            self.assertEqual(
                hashlib.sha256((self.output / item["name"]).read_bytes()).hexdigest(),
                item["sha256"],
            )

    def test_unverified_language_rejected_before_outputs(self):
        path = self.export / "download_manifest.json"
        payload = json.loads(path.read_text())
        payload["licensedSource"]["language"] = "ja"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ImportFailure):
            package_verified_export(self.export, self.output)
        self.assertFalse(self.output.exists())

    def test_missing_proof_rejected_before_outputs(self):
        path = self.export / "controller_candidate" / "rights.json"
        payload = json.loads(path.read_text())
        payload["attribution"] = "No valid evidence"
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ImportFailure):
            package_verified_export(self.export, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_results_not_overwritten(self):
        self.output.mkdir()
        marker = self.output / "private.txt"
        marker.write_text("retain")
        with self.assertRaises(ImportFailure):
            package_verified_export(self.export, self.output)
        self.assertEqual(marker.read_text(), "retain")

    def test_corrupted_epub_image_detected(self):
        pages = verified_english_pages(self.export)
        package_verified_export(self.export, self.output)
        epub = self.output / "english-fixed-layout.epub"
        raw = epub.read_bytes()
        # Deliberate EPUB archive corruption must be identified.
        epub.write_bytes(raw[:len(raw) // 2])
        with self.assertRaises((ImportFailure, OSError, zipfile.BadZipFile)):
            _verify_outputs(self.output, pages)


if __name__ == "__main__":
    unittest.main()
