"""Offline PDF source and provenance tests using synthetic, locally generated documents."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import pypdfium2 as pdfium

from manga_retriever.blackjack_pdf import import_blackjack_pdfs, main
from manga_retriever.importer import ImportFailure, verify_export


def pdf_file(path: Path, *, pages: int = 2) -> None:
    document = pdfium.PdfDocument.new()
    for index in range(pages):
        document.new_page(width=120 + index * 10, height=140)
    document.save(path)
    document.close()


class BlackJackPdfTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source = self.root / "official-pdfs"
        self.source.mkdir()
        self.out = self.root / "verified"
        self.registry = self.root / "ids.json"

    def _import(self, *, expected=1, scale=2.0):
        return import_blackjack_pdfs(self.source, self.out, self.registry,
                                    official_source_declared=True, expected_volumes=expected, scale=scale)

    def test_import_real_synthetic_pdf_and_preserve_pdf_hash_provenance(self) -> None:
        original = self.source / "01.pdf"
        pdf_file(original)
        original_hash = hashlib.sha256(original.read_bytes()).hexdigest()
        result = self._import()
        self.assertEqual(result, {"series": 1, "chapters": 1, "pages": 2})
        self.assertEqual(verify_export(self.out), result)
        manifest = json.loads((self.out / "download_manifest.json").read_text())
        provenance = manifest["sourcePdfProvenance"]
        self.assertEqual(provenance["title"], "Give My Regards to Black Jack")
        self.assertEqual(provenance["author"], "SHUHO SATO")
        self.assertEqual(provenance["volumes"][0]["sha256"], original_hash)
        self.assertFalse(provenance["originalPdfBytesPreserved"])
        self.assertFalse(provenance["publisherFileAuthenticityIndependentlyVerified"])
        self.assertEqual(original_hash, hashlib.sha256(original.read_bytes()).hexdigest())
        self.assertEqual((self.out / "controller_candidate" / "rights.json").exists(), True)

    def test_two_volumes_and_source_order(self) -> None:
        pdf_file(self.source / "Volume 10.pdf", pages=1)
        pdf_file(self.source / "Volume 2.pdf", pages=2)
        result = self._import(expected=2, scale=1.5)
        self.assertEqual(result["chapters"], 2)
        self.assertEqual(result["pages"], 3)
        manifest = json.loads((self.out / "download_manifest.json").read_text())
        self.assertEqual([r["originalFile"] for r in manifest["sourcePdfProvenance"]["volumes"]],
                         ["Volume 2.pdf", "Volume 10.pdf"])

    def test_declaration_required_before_publishing(self) -> None:
        pdf_file(self.source / "01.pdf")
        with self.assertRaisesRegex(ImportFailure, "Confirm"):
            import_blackjack_pdfs(self.source, self.out, self.registry, official_source_declared=False)
        self.assertFalse(self.out.exists())

    def test_reject_wrong_pdf_signature(self) -> None:
        (self.source / "01.pdf").write_bytes(b"not-a-real-pdf")
        with self.assertRaisesRegex(ImportFailure, "signature"):
            self._import()
        self.assertFalse(self.out.exists())

    def test_reject_corrupt_pdf_after_valid_signature(self) -> None:
        (self.source / "01.pdf").write_bytes(b"%PDF-not a valid document")
        with self.assertRaisesRegex(ImportFailure, "Unreadable"):
            self._import()
        self.assertFalse(self.out.exists())

    def test_reject_non_pdf_entries_and_mismatch(self) -> None:
        pdf_file(self.source / "01.pdf")
        (self.source / "notes.txt").write_text("not an official PDF")
        with self.assertRaises(ImportFailure):
            self._import()
        (self.source / "notes.txt").unlink()
        with self.assertRaisesRegex(ImportFailure, "matching"):
            self._import(expected=2)

    def test_no_overwrite_existing(self) -> None:
        pdf_file(self.source / "01.pdf")
        self.out.write_text("existing")
        with self.assertRaisesRegex(ImportFailure, "Destination already"):
            self._import()
        self.assertEqual(self.out.read_text(), "existing")

    def test_reject_output_or_registry_inside_source(self) -> None:
        pdf_file(self.source / "01.pdf")
        with self.assertRaisesRegex(ImportFailure, "outside"):
            import_blackjack_pdfs(self.source, self.source / "output", self.registry,
                                   official_source_declared=True)
        with self.assertRaisesRegex(ImportFailure, "outside"):
            import_blackjack_pdfs(self.source, self.out, self.source / "ids.json",
                                   official_source_declared=True)

    def test_reject_bad_scale_or_expected_volume(self) -> None:
        pdf_file(self.source / "01.pdf")
        for scale in (0.5, 1, float("inf"), 3.0):
            with self.subTest(scale=scale), self.assertRaises(ImportFailure):
                self._import(scale=scale)
        with self.assertRaises(ImportFailure):
            self._import(expected=14)

    def test_source_symlink_refused(self) -> None:
        pdf_file(self.source / "01.pdf")
        try:
            (self.source / "02.pdf").symlink_to(self.source / "01.pdf")
        except (OSError, NotImplementedError):
            self.skipTest("Windows runner did not grant symlink permission")
        with self.assertRaises(ImportFailure):
            self._import(expected=2)

    def test_cli_returns_nonzero_without_owner_declaration(self) -> None:
        pdf_file(self.source / "01.pdf")
        code = main(["--source", str(self.source), "--output", str(self.out),
                     "--registry", str(self.registry), "--expected-volumes", "1"])
        self.assertEqual(code, 1)
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
