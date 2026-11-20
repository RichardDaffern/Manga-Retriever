"""Synthetic three-manga source restrictions and verified chapter-range tests."""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from PIL import Image

from manga_retriever.selected_sources import (
    SOURCES,
    SelectedSourceError,
    audit,
    chapter_range,
    command,
    download,
    number_from_cbz,
    publish_verified,
)


def png(n: int) -> bytes:
    b = io.BytesIO()
    Image.new("RGB", (21 + n, 22 + n), (n, n, n)).save(b, format="PNG")
    return b.getvalue()


class SourcesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / "download"
        self.data.mkdir()

    def cbz(self, n: int, *, extra: str = "") -> Path:
        path = self.data / f"Vol. 1 Ch. {n}{extra}.cbz"
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("0001.png", png(n))
            z.writestr("0002.png", png(n + 1))
        return path

    def test_titles_fixed(self):
        self.assertEqual({k: v["chapters"] for k, v in SOURCES.items()}, {
            "maid-sama": 85, "last-game": 56, "onizuka-sawarida": 49,
            "love-so-life": 106,
        })

    def test_prevents_arbitrary_sources_and_oversized_batch(self):
        for slug, a, b in [("other", 1, 2), ("maid-sama", 0, 5), ("last-game", 30, 23),
                            ("onizuka-sawarida", 30, 50), ("maid-sama", 1, 21)]:
            with self.subTest(slug=slug, a=a, b=b), self.assertRaises(SelectedSourceError):
                chapter_range(slug, a, b)

    def test_fixed_original_quality_invocation(self):
        for slug, data in SOURCES.items():
            with self.subTest(slug=slug):
                cmd = command(slug, 1, 2, self.data)
                self.assertEqual(cmd[:3], [sys.executable, "-m", "mangadex_downloader"])
                self.assertIn(data["id"], cmd[3])
                self.assertIn("--language", cmd)
                self.assertNotIn("--use-compressed-image", cmd)
                self.assertNotIn("--replace", cmd)

    def test_does_not_download_without_acknowledgement(self):
        with self.assertRaises(SelectedSourceError):
            download("maid-sama", 1, 2, self.data, acknowledge_rights=False)

    def test_run_uses_argv_not_shell(self):
        proc = Mock(return_value=SimpleNamespace(returncode=0))
        download("last-game", 1, 2, self.data, acknowledge_rights=True,
                 run=proc, module_exists=lambda _: object())
        args, kw = proc.call_args
        self.assertEqual(args[0][0], sys.executable)
        self.assertEqual(kw["check"], False)
        self.assertNotIn("shell", kw)

    def test_network_failure_not_marked_complete(self):
        with self.assertRaises(SelectedSourceError):
            download("last-game", 1, 2, self.data, acknowledge_rights=True,
                     run=lambda *_a, **_k: SimpleNamespace(returncode=3), module_exists=lambda _: object())

    def test_chapter_labels_exclude_decimal_extras(self):
        self.assertEqual(number_from_cbz("Vol. 1 Ch. 12.cbz"), 12)
        self.assertIsNone(number_from_cbz("Vol. 1 Ch. 12.5.cbz"))
        self.assertIsNone(number_from_cbz("Ch. 0 Oneshot.cbz"))
        self.assertIsNone(number_from_cbz("cover.cbz"))

    def test_valid_range_full_sha_and_export(self):
        self.cbz(1)
        self.cbz(2)
        self.cbz(1, extra=".5")
        a = audit("maid-sama", 1, 2, self.data)
        self.assertEqual(a["verifiedMainChapterNumbers"], [1, 2])
        self.assertEqual(a["verifiedMainChapters"], 2)
        self.assertEqual(a["verifiedArchives"], 3)
        self.assertEqual(a["verifiedPages"], 6)
        target = self.root / "verified"
        publish_verified(self.data, a, target)
        self.assertTrue((target / "quality_audit.json").is_file())
        self.assertEqual(len(list((target / "chapters").rglob("*.cbz"))), 3)
        with self.assertRaises(SelectedSourceError):
            publish_verified(self.data, a, target)

    def test_missing_main_not_masked_by_extras(self):
        self.cbz(1)
        self.cbz(1, extra=".5")
        with self.assertRaisesRegex(SelectedSourceError, "Missing numbered chapters"):
            audit("last-game", 1, 2, self.data)

    def test_chapter_zero_oneshot_is_verified_extra_without_masking_missing_main(self):
        self.cbz(1)
        oneshot = self.data / "Ch. 0 Oneshot.cbz"
        with zipfile.ZipFile(oneshot, "w") as archive:
            archive.writestr("0001.png", png(2))
        report = audit("onizuka-sawarida", 1, 1, self.data)
        self.assertEqual(report["verifiedMainChapterNumbers"], [1])
        self.assertEqual(report["verifiedArchives"], 2)
        self.assertEqual(report["extraChapterArchivePaths"], ["Ch. 0 Oneshot.cbz"])
        with self.assertRaisesRegex(SelectedSourceError, "Missing numbered chapters"):
            audit("onizuka-sawarida", 1, 2, self.data)

    def test_duplicate_chapter_rejected(self):
        self.cbz(1)
        with zipfile.ZipFile(self.data / "Vol. 2 Ch. 1.cbz", "w") as z:
            z.writestr("0001.png", png(4))
        with self.assertRaisesRegex(SelectedSourceError, "Duplicate"):
            audit("onizuka-sawarida", 1, 1, self.data)

    def test_bad_image_does_not_publish(self):
        with zipfile.ZipFile(self.data / "Vol. 1 Ch. 1.cbz", "w") as z:
            z.writestr("0001.png", b"not-an-image")
        with self.assertRaises(SelectedSourceError):
            audit("maid-sama", 1, 1, self.data)

    def test_source_output_symlinks_not_accepted(self):
        self.cbz(1)
        link = self.data / "Ch. 1 linked.cbz"
        try:
            link.symlink_to(self.data / "Vol. 1 Ch. 1.cbz")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this runner")
        with self.assertRaises(SelectedSourceError):
            audit("maid-sama", 1, 1, self.data)


if __name__ == "__main__":
    unittest.main()
