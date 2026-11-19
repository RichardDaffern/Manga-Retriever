"""Synthetic image-quality and controlled-source URL tests; no external artwork."""
from __future__ import annotations

import io
import unittest

from PIL import Image

from scripts.love_kainushi_quality import (
    MAX_BYTES,
    check_mangadex_host,
    image_stats,
    image_url,
    sample_chapter,
)


class QualityProbeTests(unittest.TestCase):
    def test_mangadex_at_home_host_validation(self):
        self.assertEqual(check_mangadex_host("https://a1b2.mangadex.network/t"), "https://a1b2.mangadex.network/t")
        for url in ("http://x.mangadex.network", "https://evil.example", "https://mangadex.network.evil.org",
                    "https://user:pass@foo.mangadex.network", "https://foo.mangadex.network:4443"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                check_mangadex_host(url)

    def test_page_url_bounds(self):
        sha = "a" * 32
        url = image_url("https://node.mangadex.network/token", sha, "x1-cover.png", "data")
        self.assertEqual(url, "https://node.mangadex.network/token/data/" + sha + "/x1-cover.png")
        for filename in ("../x.png", "x/1.png", "%2Fsecret", ""):
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                image_url("https://node.mangadex.network", sha, filename, "data")
        with self.assertRaises(ValueError):
            image_url("https://node.mangadex.network", sha, "x.png", "bad-mode")

    def test_png_dimensions_and_hash(self):
        buffer = io.BytesIO()
        Image.new("RGB", (20, 30)).save(buffer, format="PNG")
        report = image_stats(buffer.getvalue())
        self.assertEqual(report["width"], 20)
        self.assertEqual(report["height"], 30)
        self.assertEqual(report["pixelCount"], 600)
        self.assertEqual(report["format"], "PNG")
        self.assertEqual(len(report["sha256"]), 64)

    def test_corruption_or_excessive_size_not_verified(self):
        with self.assertRaises(ValueError):
            image_stats(b"")
        with self.assertRaises(OSError):
            image_stats(b"Not an image")
        with self.assertRaises(ValueError):
            image_stats(b"A" * (MAX_BYTES + 1))

    def test_missing_image_manifest_rejected(self):
        class Client:
            def request(self, _):
                return {"chapter": {"data": [], "dataSaver": []}}
        with self.assertRaises(ValueError):
            sample_chapter(Client(), "1", "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


if __name__ == "__main__":
    unittest.main()
