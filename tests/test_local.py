"""All test images are generated in memory. No third-party manga in CI."""

import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from manga_retriever.cli import main
from manga_retriever.importer import ImportFailure, import_local, verify_export


def png(colour: tuple[int, int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (12, 16), colour).save(buffer, format="PNG")
    return buffer.getvalue()


class LocalImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = tempfile.TemporaryDirectory()
        self.addCleanup(self.context.cleanup)
        self.root = Path(self.context.name)
        self.source = self.root / "source"
        self.output = self.root / "output"
        self.registry = self.root / "ids.json"
        self.source.mkdir()

    def _chapter(self) -> Path:
        chapter = self.source / "Original" / "Chapter 2"
        chapter.mkdir(parents=True)
        (chapter / "10.png").write_bytes(png((10, 20, 30)))
        (chapter / "2.png").write_bytes(png((40, 50, 60)))
        (chapter / "1.png").write_bytes(png((70, 80, 90)))
        return chapter

    def test_folder_natural_order_and_controller_contract(self) -> None:
        self._chapter()
        result = import_local(self.source, self.output, self.registry)
        self.assertEqual(result, {"series": 1, "chapters": 1, "pages": 3})
        candidate = self.output / "controller_candidate"
        catalogue = json.loads((candidate / "catalogue.json").read_text())
        self.assertEqual(catalogue[0]["title"], "Original")
        self.assertEqual(catalogue[0]["chapters"][0]["sequence"], 0)
        chapter_id = catalogue[0]["chapters"][0]["id"]
        manifest = json.loads((candidate / "manifests" / (chapter_id + ".json")).read_text())
        self.assertEqual(manifest["schemaVersion"], 1)
        self.assertEqual(manifest["mediaKind"], "manga")
        self.assertTrue(all(p["id"].startswith("pg_") for p in manifest["pages"]))
        self.assertTrue(all(p["assetPath"].startswith("manga/mng_") for p in manifest["pages"]))
        with zipfile.ZipFile(self.output / "chapters" / (chapter_id + ".cbz")) as cbz:
            self.assertEqual(cbz.namelist(), ["0001.png", "0002.png", "0003.png"])
            self.assertEqual(cbz.read("0001.png"), png((70, 80, 90)))
        self.assertEqual(verify_export(self.output), result)

    def test_archive_and_identity_survive_repeat_import(self) -> None:
        archive = self.source / "One.cbz"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("10.png", png((1, 2, 3)))
            z.writestr("2.png", png((4, 5, 6)))
        import_local(archive, self.output, self.registry)
        first_ids = json.loads(self.registry.read_text())
        import_local(archive, self.root / "output2", self.registry)
        self.assertEqual(json.loads(self.registry.read_text()), first_ids)
        self.assertEqual(verify_export(self.root / "output2")["pages"], 2)

    def test_rejects_traversal_and_does_not_publish(self) -> None:
        archive = self.source / "Bad.cbz"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("../outside.png", png((2, 3, 4)))
        with self.assertRaises(ImportFailure):
            import_local(archive, self.output, self.registry)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.registry.exists())

    def test_rejects_fake_png_and_duplicate_pages(self) -> None:
        chapter = self._chapter()
        (chapter / "1.png").write_bytes(b"<html>not image</html>")
        with self.assertRaises(ImportFailure):
            import_local(self.source, self.output, self.registry)
        (chapter / "1.png").write_bytes(png((40, 50, 60)))
        with self.assertRaises(ImportFailure):
            import_local(self.source, self.output, self.registry)

    def test_rejects_corrupted_candidate(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        asset = next((self.output / "controller_candidate" / "assets").rglob("*.png"))
        asset.write_bytes(b"broken")
        with self.assertRaises(ImportFailure):
            verify_export(self.output)

    def test_no_overwrite(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        with self.assertRaises(ImportFailure):
            import_local(self.source, self.output, self.registry)

    def test_malformed_rights_fail_closed(self) -> None:
        self._chapter()
        rights = self.root / "rights.json"
        rights.write_text('{"schemaVersion":2}')
        with self.assertRaises(ImportFailure):
            import_local(self.source, self.output, self.registry, rights_path=rights)

    def test_command_line(self) -> None:
        self._chapter()
        self.assertEqual(main(["import", "--source", str(self.source), "--output", str(self.output),
                               "--registry", str(self.registry)]), 0)
        self.assertEqual(main(["verify", "--export", str(self.output)]), 0)

    def test_archive_ratio_limit(self) -> None:
        archive = self.source / "Large.cbz"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("1.png", b"0" * 100000)
        with self.assertRaises(ImportFailure):
            import_local(archive, self.output, self.registry)

    def test_missing_numbers_warning(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        inventory = json.loads((self.output / "controller_candidate" / "inventory.json").read_text())
        self.assertIn("Missing numbered page(s) in Original/Chapter 2", inventory["warnings"])


    def test_missing_cbz_is_not_complete(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        next((self.output / "chapters").glob("*.cbz")).unlink()
        with self.assertRaises(ImportFailure):
            verify_export(self.output)

    def test_malformed_cbz_reports_import_failure(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        next((self.output / "chapters").glob("*.cbz")).write_bytes(b"not a zip")
        with self.assertRaises(ImportFailure):
            verify_export(self.output)

    def test_unexpected_cbz_member_is_rejected(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        cbz = next((self.output / "chapters").glob("*.cbz"))
        with zipfile.ZipFile(cbz, "a") as archive:
            archive.writestr("unlisted.png", png((1, 0, 1)))
        with self.assertRaises(ImportFailure):
            verify_export(self.output)

    def test_tampered_page_identity_is_rejected(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        path = next((self.output / "controller_candidate" / "manifests").glob("*.json"))
        manifest = json.loads(path.read_text())
        manifest["pages"][0]["id"] = "pg_modifiedfake00000000"
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ImportFailure):
            verify_export(self.output)

    def test_orphaned_file_is_rejected(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        (self.output / "controller_candidate" / "assets" / "stray.txt").write_text("orphan")
        with self.assertRaises(ImportFailure):
            verify_export(self.output)

    def test_mutated_rights_status_is_rejected(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        path = self.output / "controller_candidate" / "inventory.json"
        inventory = json.loads(path.read_text())
        inventory["rightsVerified"] = True
        path.write_text(json.dumps(inventory))
        with self.assertRaises(ImportFailure):
            verify_export(self.output)

    def test_reordered_chapters_are_rejected(self) -> None:
        self._chapter()
        import_local(self.source, self.output, self.registry)
        path = self.output / "controller_candidate" / "catalogue.json"
        catalogue = json.loads(path.read_text())
        catalogue[0]["chapters"][0]["sequence"] = 9
        path.write_text(json.dumps(catalogue))
        with self.assertRaises(ImportFailure):
            verify_export(self.output)


if __name__ == "__main__":
    unittest.main()
