"""Offline checks for five fixed manga cover image retrieval and validation."""
from __future__ import annotations

import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from scripts.download_existing_five_covers import COVERS, _image, build


class Response:
    status = 200

    def __init__(self, url, image, *, reported_url=None):
        self.url = reported_url or url
        self.image = image

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def geturl(self):
        return self.url

    def read(self, maximum):
        return self.image


def fake_bytes(fmt):
    picture = Image.effect_noise((410, 610), 80).convert("RGB")
    stream = io.BytesIO()
    picture.save(stream, format=fmt)
    return stream.getvalue()


class CoverDownloadTests(unittest.TestCase):
    def setUp(self):
        self.png = fake_bytes("PNG")
        self.jpg = fake_bytes("JPEG")

    def opener(self, request, *, timeout):
        self.assertEqual(timeout, 25)
        url = request.full_url
        self.assertIn(url, COVERS.values())
        return Response(url, self.png if url.endswith(".png") else self.jpg)

    def test_only_five_pinned_titles(self):
        self.assertEqual(len(COVERS), 5)
        for url in COVERS.values():
            self.assertTrue(url.startswith("https://uploads.mangadex.org/covers/"))

    def test_all_five_covers_are_original_image_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "images.zip"
            report = build(out, opener=self.opener, pause=lambda _: None)
            self.assertEqual(report["count"], 5)
            self.assertFalse(report["privateHuggingFaceModified"])
            with zipfile.ZipFile(out) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(len(z.namelist()), 6)
                for slug, url in COVERS.items():
                    record = next(x for x in report["covers"] if x["slug"] == slug)
                    data = z.read(record["path"])
                    self.assertEqual(data, self.png if url.endswith(".png") else self.jpg)
                    self.assertGreaterEqual(record["width"], 240)
                self.assertEqual(json.loads(z.read("cover-attachment-manifest.json"))["count"], 5)

    def test_redirect_and_invalid_image_rejected(self):
        slug, url = next(iter(COVERS.items()))
        with self.assertRaisesRegex(ValueError, "Unexpected cover host"):
            _image(slug, url, opener=lambda request, **kwargs:
                   Response(url, self.jpg, reported_url="https://evil.example/img.jpg"))
        with self.assertRaisesRegex(ValueError, "Missing or oversized"):
            _image(slug, url, opener=lambda request, **kwargs: Response(url, b"broken"))

    def test_refuses_to_overwrite_existing_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "images.zip"
            target.write_text("keep existing bundle")
            with self.assertRaisesRegex(ValueError, "must not be overwritten"):
                build(target, opener=self.opener, pause=lambda _: None)
            self.assertEqual(target.read_text(), "keep existing bundle")


if __name__ == "__main__":
    unittest.main()
