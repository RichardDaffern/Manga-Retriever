"""Synthetic validation of fractional manga chapter batch boundaries and safety."""
from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from scripts.kainushi_partial import (
    MANGA_ID,
    PartialSourceError,
    chapter_filename_label,
    command,
    inspect_and_stage,
    range_labels,
    run_batch,
)


class KainushiBatchTests(unittest.TestCase):
    def test_fixed_fractional_batch_membership(self):
        labels = ["1", "1.2", "9.2", "10.1", "18.2", "19", "25.5"]
        self.assertEqual(range_labels(labels, 1, 10), ["1", "1.2", "9.2"])
        self.assertEqual(range_labels(labels, 10, 19), ["10.1", "18.2"])
        self.assertEqual(range_labels(labels, 19, 26), ["19", "25.5"])
        with self.assertRaises(PartialSourceError):
            range_labels(labels, 0, 100)

    def test_decimal_labels_not_collapsed(self):
        self.assertEqual(chapter_filename_label(Path("Vol. 2 Ch. 12.1.cbz")), "12.1")
        self.assertEqual(chapter_filename_label(Path("Vol. 2 Ch. 12.cbz")), "12")
        self.assertIsNone(chapter_filename_label(Path("cover.cbz")))

    def test_command_fixed_title_and_exact_decimal_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = command("10.1", "18.2", Path(tmp))
            self.assertIn(MANGA_ID, args[3])
            self.assertEqual(args[args.index("--start-chapter") + 1], "10.1")
            self.assertEqual(args[args.index("--end-chapter") + 1], "18.2")
            self.assertNotIn("--use-compressed-image", args)
            with self.assertRaises(PartialSourceError):
                command("../bad", "18.2", Path(tmp))

    def test_run_batch_uses_approved_metadata_and_no_shell(self):
        class FakeClient:
            def feed(self, _id):
                return 2, [
                    {"id": "x", "attributes": {"chapter": "10.1", "volume": "1"}},
                    {"id": "y", "attributes": {"chapter": "18.2", "volume": "1"}},
                ]

        def png() -> bytes:
            payload = io.BytesIO()
            Image.new("RGB", (24, 30)).save(payload, format="PNG")
            return payload.getvalue()

        with tempfile.TemporaryDirectory() as tmp:
            source, verified = Path(tmp) / "downloads", Path(tmp) / "verified"

            def run(argv, *, check):
                self.assertFalse(check)
                self.assertEqual(argv[1:3], ["-m", "mangadex_downloader"])
                self.assertIn("--end-chapter", argv)
                for label in ("10.1", "18.2"):
                    path = source / f"Vol. 1 Ch. {label}.cbz"
                    with zipfile.ZipFile(path, "w") as archive:
                        archive.writestr("0001.png", png())
                return SimpleNamespace(returncode=0)

            report = run_batch(2, source, verified, client=FakeClient(), runner=run,
                               module_exists=lambda _name: True)
            self.assertTrue(report["completeAgainstMangaDexRequestedBatch"])
            self.assertEqual(report["verifiedLabels"], ["10.1", "18.2"])
            self.assertEqual(report["verifiedImagePages"], 2)
            self.assertFalse(report["completeOriginalManga"])
            self.assertTrue((verified / "quality_audit.json").is_file())

    def test_missing_fractional_and_duplicate_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "downloads"
            folder.mkdir()
            report = inspect_and_stage(
                folder, Path(tmp) / "verified", ["1.1", "1.2"],
                client_return_code=1, source_labels=["1.1", "1.2"],
            )
            self.assertEqual(report["missingLabelsWithinRequestedBatch"], ["1.1", "1.2"])
            self.assertFalse(report["completeAgainstMangaDexRequestedBatch"])


if __name__ == "__main__":
    unittest.main()
