"""Synthetic-only Love So Life five-bonus chapter safety and export tests."""
from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from scripts.love_so_life_extras import BONUS_LABELS, BonusError, command, find_bonus_chapters, run_bonuses


def row(label: str, chapter_id: str, *, external: str | None = None) -> dict:
    return {"id": chapter_id, "attributes": {"chapter": label, "externalUrl": external}}


class LoveSoLifeBonusTests(unittest.TestCase):
    def test_fixed_five_decimal_extras(self):
        self.assertEqual(BONUS_LABELS, ("33.5", "33.6", "63.5", "75.5", "99.5"))

    def test_fan_external_link_not_selected(self):
        records = [row("33.5", "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", external="https://site.test"),
                   row("33.5", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")]
        self.assertEqual(find_bonus_chapters(records)["33.5"], "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

    def test_only_fixed_chapter_id_accepts(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = command("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", Path(tmp))
            self.assertIn("https://mangadex.org/chapter/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", args)
            self.assertNotIn("--use-compressed-image", args)
            with self.assertRaises(BonusError):
                command("https://evil.test/test", Path(tmp))

    def test_verified_five_synthetic_chapter_cbzs(self):
        ids = [f"{idx:08x}-aaaa-aaaa-aaaa-aaaaaaaaaaaa" for idx in range(1, 6)]
        class Client:
            def feed(self, _title):
                return 5, [row(label, ids[i]) for i, label in enumerate(BONUS_LABELS)]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "source"
            verified = Path(tmp) / "verified"

            def runner(argv, *, check):
                self.assertFalse(check)
                label = BONUS_LABELS[ids.index(argv[3].split("/")[-1])]
                chapter = out / label / f"Vol. 1 Ch. {label}.cbz"
                data = io.BytesIO()
                Image.new("RGB", (20, 30)).save(data, format="PNG")
                with zipfile.ZipFile(chapter, "w") as archive:
                    archive.writestr("001.png", data.getvalue())
                return SimpleNamespace(returncode=0)

            report = run_bonuses(out, verified, client=Client(), runner=runner,
                                 module_exists=lambda _mod: True)
            self.assertTrue(report["allFiveExtrasVerified"])
            self.assertEqual(report["missingDecimalExtras"], [])
            self.assertEqual(len(report["archives"]), 5)
            self.assertEqual(len(list((verified / "chapters").rglob("*.cbz"))), 5)
            with self.assertRaises(BonusError):
                run_bonuses(out, verified, client=Client(), runner=runner,
                            module_exists=lambda _mod: True)


if __name__ == "__main__":
    unittest.main()
