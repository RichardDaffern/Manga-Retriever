"""Offline tests for locally retained chapter-1 manga URL downloads."""
from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from scripts.five_manga_catalogue import SOURCES
from scripts.local_url_manga_download import (
    ChapterPilotError,
    _check_listing,
    chapter_selection,
    inspect_media,
    planned_command,
    run_pilot,
    source_for_url,
)


def _png() -> bytes:
    buf = io.BytesIO()
    Image.effect_noise((350, 500), 70).convert("RGB").save(buf, "PNG")
    return buf.getvalue()


class URLChapterPilotTests(unittest.TestCase):
    def test_six_exact_source_urls_only(self):
        self.assertEqual(len(SOURCES), 6)
        for slug, source in SOURCES.items():
            self.assertEqual(source_for_url(source["url"])[0], slug)
        for bad in [
            "http://mangakatana.com/manga/nisekoi.553",
            "https://mangakatana.com.evil.com/manga/nisekoi.553",
            "https://mangakatana.com/manga/nisekoi.553?redirect=x",
            "https://weebcentral.com/series/unknown",
            "https://mangakatana.com/manga/something-else.333",
            "https://mangakatana.com/manga/nisekoi.553/download",
        ]:
            with self.subTest(bad=bad), self.assertRaises(ChapterPilotError):
                source_for_url(bad)

    def test_bounded_selection_and_real_cli_flags(self):
        for invalid in ["all", "1-30", "0", "1,2", "2-1", "99-123", "--help"]:
            with self.subTest(invalid=invalid), self.assertRaises(ChapterPilotError):
                chapter_selection(invalid, 100)
        command = planned_command("manga-downloader", SOURCES["nisekoi"]["url"],
                                  "1-3", Path("output"))
        self.assertIn("--output-dir", command)
        self.assertIn("--convert-images", command)
        self.assertIn("none", command)
        self.assertIn("--language", command)
        self.assertIn("en", command)
        self.assertIn("--skip-existing", command)
        self.assertEqual(command[-1], "1-3")

    def test_missing_english_label_is_explicitly_unverified(self):
        data = {"title": "Love Hina", "chapters": [
            {"number": 1, "title": "Chapter 1"},
            {"number": 2, "title": "Chapter 2"},
        ]}
        out = _check_listing("love-hina", data, "1-2")
        self.assertTrue(out["requiresManualEnglishReview"])
        self.assertFalse(out["sourceHasExplicitEnglishLabels"])
        data["chapters"][0]["language"] = "ja"
        with self.assertRaisesRegex(ChapterPilotError, "non-English"):
            _check_listing("love-hina", data, "1-2")
        data["chapters"][0]["language"] = "en"
        data["chapters"][1]["language"] = "en"
        self.assertFalse(_check_listing("love-hina", data, "1-2")[
            "requiresManualEnglishReview"
        ])

    def test_pilot_downloads_real_cbz_and_uses_verified_archive(self):
        with tempfile.TemporaryDirectory() as home:
            dest = Path(home) / "test-download"
            source = SOURCES["love-hina"]

            def runner(argv, **kwargs):
                if len(argv) > 1 and argv[1] == "list":
                    return subprocess.CompletedProcess(argv, 0, json.dumps({
                        "title": source["title"],
                        "chapters": [{"number": 1, "language": "en"}],
                    }), "")
                self.assertIn("--output-dir", argv)
                folder = Path(argv[argv.index("--output-dir") + 1])
                page = _png()
                with zipfile.ZipFile(folder / "Love Hina 1 - Chapter 1.cbz", "w") as archive:
                    archive.writestr("0001.png", page, compress_type=zipfile.ZIP_STORED)
                return subprocess.CompletedProcess(argv, 0, "downloaded", "")

            outcome = run_pilot(source["url"], "1", dest, client=sys.executable,
                                runner=runner, acknowledge_local_rights=True)
            self.assertEqual(outcome["verifiedArchiveCount"], 1)
            self.assertEqual(outcome["verifiedPages"], 1)
            self.assertFalse(outcome["requiresManualEnglishReview"])
            self.assertTrue((dest / "download-report.json").exists())
            self.assertEqual(inspect_media(dest, max_archives=3)["verifiedPages"], 1)
            self.assertEqual(len(list(dest.glob("*.cbz"))), 1)

    def test_bad_source_or_failed_download_never_publishes(self):
        with tempfile.TemporaryDirectory() as home:
            dest = Path(home) / "test-download"
            source = SOURCES["nisekoi"]
            with self.assertRaisesRegex(ChapterPilotError, "Confirm source"):
                run_pilot(source["url"], "1", dest, client=sys.executable)
            self.assertFalse(dest.exists())
            bad = {"title": "Unrelated Manga", "chapters": [{"number": 1}]}

            def runner(argv, **kwargs):
                return subprocess.CompletedProcess(argv, 0, json.dumps(bad), "")

            with self.assertRaisesRegex(ChapterPilotError, "does not match"):
                run_pilot(source["url"], "1", dest, client=sys.executable,
                          runner=runner, acknowledge_local_rights=True)
            self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
