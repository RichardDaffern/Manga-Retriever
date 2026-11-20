"""Synthetic, offline end-to-end checks for DRM-free English manga EPUB import."""
from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from manga_retriever.alternative_formats import package_verified_export
from manga_retriever.epub_import import import_epubs
from manga_retriever.importer import ImportFailure, verify_export
from manga_retriever.peppercarrot import LICENCE_URL, SOURCE_PAGE, download_episode_26

PAGE_ROOT = (
    "https://www.peppercarrot.com/0_sources/ep26_Books-Are-Great/hi-res/"
    "en_Pepper-and-Carrot_by-David-Revoy_E26P"
)


def sample_jpeg(n: int) -> bytes:
    target = io.BytesIO()
    Image.new("RGB", (45 + n, 50 + n), (n * 30, 15, 34)).save(target, "JPEG")
    return target.getvalue()


def fake_html() -> bytes:
    links = "".join(f'<a href="{PAGE_ROOT}{n:02d}.jpg">Page {n}</a>' for n in range(1, 7))
    return (f'<h1>Episode 26: Books Are Great</h1><span>David Revoy</span>'
            f'<a href="{LICENCE_URL}">CC BY 4.0</a>{links}').encode()


def rewrite_epub(path: Path, name: str, content: bytes) -> None:
    replacement = path.with_suffix(".new")
    with zipfile.ZipFile(path) as old, zipfile.ZipFile(replacement, "w") as new:
        for member in old.infolist():
            new.writestr(member, content if member.filename == name else old.read(member))
    replacement.replace(path)


class EnglishEpubImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.raw = {n: sample_jpeg(n) for n in range(1, 7)}

        def fetch(url: str, _limit: int) -> bytes:
            if url == SOURCE_PAGE:
                return fake_html()
            if url.startswith(PAGE_ROOT) and url.endswith(".jpg"):
                return self.raw[int(url[-6:-4])]
            raise AssertionError("Unexpected remote path")

        export = self.base / "source"
        self.assertEqual(download_episode_26(export, self.base / "original_ids.json",
                                             fetch=fetch, sleep=lambda _: None)["pages"], 6)
        packaged = self.base / "packaged"
        package_verified_export(export, packaged)
        self.epub = packaged / "english-fixed-layout.epub"
        self.output = self.base / "output"

    def test_import_retains_every_original_image_byte_and_stable_ids(self):
        result = import_epubs(self.epub, self.output, self.base / "ids.json", acknowledge_rights=True)
        self.assertEqual(result["format"], "epub")
        self.assertEqual(result["language"], "en")
        self.assertEqual(result["chapters"], 1)
        self.assertEqual(result["pages"], 6)
        self.assertEqual(verify_export(self.output)["pages"], 6)
        original_hashes = {hashlib.sha256(item).hexdigest() for item in self.raw.values()}
        contents = list((self.output / "controller_candidate" / "assets").rglob("*.jpg"))
        self.assertEqual({hashlib.sha256(p.read_bytes()).hexdigest() for p in contents}, original_hashes)
        self.assertEqual(len(list((self.output / "chapters").glob("*.cbz"))), 1)
        catalogue = json.loads((self.output / "controller_candidate" / "catalogue.json").read_text())
        self.assertEqual(catalogue[0]["direction"], "rtl")

    def test_two_volume_import_is_safe_and_complete(self):
        series = self.base / "epubs"
        series.mkdir()
        (series / "Love Story Vol 1.epub").write_bytes(self.epub.read_bytes())
        (series / "Love Story Vol 2.epub").write_bytes(self.epub.read_bytes())
        result = import_epubs(series, self.output, self.base / "ids.json",
                              series_title="Sample English Manga", acknowledge_rights=True)
        self.assertEqual((result["series"], result["chapters"], result["pages"]), (1, 2, 12))
        self.assertEqual(verify_export(self.output)["pages"], 12)

    def test_japanese_language_is_rejected(self):
        with zipfile.ZipFile(self.epub) as archive:
            original = archive.read("EPUB/package.opf")
        changed = original.replace(b"<dc:language>en</dc:language>",
                                   b"<dc:language>ja</dc:language>")
        self.assertNotEqual(original, changed)
        rewrite_epub(self.epub, "EPUB/package.opf", changed)
        with self.assertRaisesRegex(ImportFailure, "Only explicitly English"):
            import_epubs(self.epub, self.output, self.base / "ids.json", acknowledge_rights=True)
        self.assertFalse(self.output.exists())

    def test_encryption_metadata_rejected(self):
        with zipfile.ZipFile(self.epub, "a") as archive:
            archive.writestr("META-INF/encryption.xml", "<encrypted/>")
        with self.assertRaisesRegex(ImportFailure, "DRM/encrypted"):
            import_epubs(self.epub, self.output, self.base / "ids.json", acknowledge_rights=True)
        self.assertFalse(self.output.exists())

    def test_external_images_rejected(self):
        with zipfile.ZipFile(self.epub) as archive:
            data = archive.read("EPUB/pages/p0001.xhtml")
        altered = data.replace(b"../images/p0001.jpg", b"https://example.org/p.jpg")
        self.assertNotEqual(data, altered)
        rewrite_epub(self.epub, "EPUB/pages/p0001.xhtml", altered)
        with self.assertRaisesRegex(ImportFailure, "External or ambiguous"):
            import_epubs(self.epub, self.output, self.base / "ids.json", acknowledge_rights=True)

    def test_path_escape_fails_closed(self):
        with zipfile.ZipFile(self.epub, "a") as archive:
            archive.writestr("../escape.jpg", b"fake image")
        with self.assertRaisesRegex(ImportFailure, "Unsafe"):
            import_epubs(self.epub, self.output, self.base / "ids.json", acknowledge_rights=True)

    def test_no_permission_declaration_or_overwrite(self):
        with self.assertRaisesRegex(ImportFailure, "authorised"):
            import_epubs(self.epub, self.output, self.base / "ids.json")
        self.output.mkdir()
        marker = self.output / "keep.txt"
        marker.write_text("important")
        with self.assertRaisesRegex(ImportFailure, "destination already exists"):
            import_epubs(self.epub, self.output, self.base / "ids.json", acknowledge_rights=True)
        self.assertEqual(marker.read_text(), "important")


if __name__ == "__main__":
    unittest.main()
