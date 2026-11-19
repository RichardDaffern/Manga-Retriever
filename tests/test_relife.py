"""Synthetic offline tests for the exact-title private ReLIFE retrieval workflow."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from PIL import Image

from manga_retriever.relife import (
    EXPECTED_NUMBERED_CHAPTERS,
    ReLIFEError,
    _inspect_cbz,
    audit_download,
    download,
    main,
    planned_command,
)


def png(seed: int) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (16 + seed, 22 + seed), (seed, seed, seed)).save(buffer, format="PNG")
    return buffer.getvalue()


class ReLifeTests(unittest.TestCase):
    def setUp(self) -> None:
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.folder = self.root / "manga"
        self.folder.mkdir()

    def cbz(self, name="Chapter-001.cbz") -> Path:
        path = self.folder / name
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("001.png", png(1))
            archive.writestr("002.png", png(2))
            archive.writestr("ComicInfo.xml", b"<ComicInfo><Title>Sample</Title></ComicInfo>")
        return path

    def test_original_quality_command_and_fixed_title(self) -> None:
        argv = planned_command(self.folder, 1, EXPECTED_NUMBERED_CHAPTERS)
        self.assertEqual(argv[0], "mangadex-dl")
        self.assertIn("6e3553b9-ddb5-4d37-b7a3-99998044774e", argv[1])
        self.assertIn("--language", argv)
        self.assertIn("en", argv)
        self.assertIn("cbz", argv)
        self.assertNotIn("--use-compressed-image", argv)
        self.assertIn("--delay-requests", argv)
        self.assertNotIn("--replace", argv)

    def test_bad_range_fails_closed(self) -> None:
        for start, end in ((0, 1), (2, 1), (1, 223), (-10, 1)):
            with self.subTest(start=start, end=end), self.assertRaises(ReLIFEError):
                planned_command(self.folder, start, end)

    def test_requires_rights_acknowledgement(self) -> None:
        with self.assertRaisesRegex(ReLIFEError, "personal use"):
            download(self.folder, 1, 2, acknowledge_rights=False)

    def test_missing_downloader_actionable(self) -> None:
        with self.assertRaisesRegex(ReLIFEError, "Install"):
            download(self.folder, 1, 2, acknowledge_rights=True,
                     executable_exists=lambda _: None)

    def test_constructs_arg_list_not_shell(self) -> None:
        proc = Mock(return_value=SimpleNamespace(returncode=0))
        download(self.folder, 1, 2, acknowledge_rights=True, run=proc,
                 executable_exists=lambda _: "/usr/local/bin/mangadex-dl")
        args, kwargs = proc.call_args
        self.assertEqual(args[0][0], "mangadex-dl")
        self.assertFalse(kwargs["check"])
        self.assertNotIn("shell", kwargs)

    def test_partial_failure_not_marked_success(self) -> None:
        with self.assertRaisesRegex(ReLIFEError, "partial files"):
            download(self.folder, 1, 2, acknowledge_rights=True,
                     run=lambda *_a, **_k: SimpleNamespace(returncode=2),
                     executable_exists=lambda _: "/fake/client")

    def test_verified_full_quality_audit_contains_checksums(self) -> None:
        self.cbz()
        result = audit_download(self.folder)
        self.assertEqual(result["verifiedArchives"], 1)
        self.assertEqual(result["verifiedPages"], 2)
        self.assertEqual(result["archives"][0]["pages"][0]["width"], 17)
        self.assertEqual(len(result["archives"][0]["sha256"]), 64)
        self.assertFalse(result["completeSeriesVerified"])
        self.assertEqual(result["requestedQuality"], "source-original-not-data-saver")

    def test_audit_only_cli_writes_private_report(self) -> None:
        self.cbz()
        target = self.root / "audit.json"
        self.assertEqual(main(["--mode", "audit", "--output", str(self.folder), "--report", str(target)]), 0)
        self.assertEqual(json.loads(target.read_text())["verifiedPages"], 2)

    def test_corrupt_png_does_not_pass(self) -> None:
        with zipfile.ZipFile(self.folder / "bad.cbz", "w") as z:
            z.writestr("001.png", b"not an image")
        with self.assertRaises(ReLIFEError):
            audit_download(self.folder)

    def test_zip_traversal_is_rejected(self) -> None:
        with zipfile.ZipFile(self.folder / "bad.cbz", "w") as z:
            z.writestr("../outside.png", png(2))
        with self.assertRaises(ReLIFEError):
            audit_download(self.folder)

    def test_rejects_duplicate_members(self) -> None:
        with zipfile.ZipFile(self.folder / "dup.cbz", "w") as z:
            z.writestr("001.png", png(1))
            z.writestr("001.png", png(2))
        with self.assertRaises(ReLIFEError):
            audit_download(self.folder)

    def test_rejects_nonimage_member(self) -> None:
        with zipfile.ZipFile(self.folder / "odd.cbz", "w") as z:
            z.writestr("001.png", png(1))
            z.writestr("license.exe", b"unsafe")
        with self.assertRaises(ReLIFEError):
            audit_download(self.folder)

    def test_rejects_symlinks(self) -> None:
        original = self.cbz()
        link = self.folder / "linked.cbz"
        try:
            link.symlink_to(original)
        except (OSError, NotImplementedError):
            self.skipTest("Test runner lacks symlink permission")
        with self.assertRaises(ReLIFEError):
            audit_download(self.folder)

    def test_empty_output_does_not_claim_success(self) -> None:
        with self.assertRaisesRegex(ReLIFEError, "No CBZ"):
            audit_download(self.folder)

    def test_inspect_cbz_individual(self) -> None:
        cbz = self.cbz()
        self.assertEqual(_inspect_cbz(cbz)["verifiedPageCount"], 2)


if __name__ == "__main__":
    unittest.main()
