"""Cross-repository acceptance tests using only newly generated synthetic pages.

These tests are skipped in the standard Retriever-only unit suite. The dedicated
CI contract job installs an immutable Controller revision and runs them for real.
No dataset token, remote storage or third-party artwork is involved.
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from manga_retriever.importer import ImportFailure, import_local, verify_export


def original_png(colour: tuple[int, int, int]) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (18, 24), colour).save(output, format="PNG")
    return output.getvalue()


@unittest.skipUnless(importlib.util.find_spec("taiyou_manga"), "Controller is installed only in the cross-repo CI job")
class ControllerCandidateAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.source = self.root / "source"
        self.registry = self.root / "private-ids.json"
        for chapter, colours in (
            ("Chapter 1", ((10, 20, 30), (40, 50, 60))),
            ("Chapter 2", ((70, 80, 90),)),
        ):
            directory = self.source / "Synthetic Original" / chapter
            directory.mkdir(parents=True)
            for index, colour in enumerate(colours, start=1):
                (directory / f"{index:04d}.png").write_bytes(original_png(colour))

    def _export(self, name: str = "export", rights_path: Path | None = None) -> Path:
        output = self.root / name
        self.assertEqual(
            import_local(self.source, output, self.registry, rights_path=rights_path),
            {"series": 1, "chapters": 2, "pages": 3},
        )
        return output

    def test_controller_accepts_original_bytes_and_stable_ids(self) -> None:
        from taiyou_manga.builder import verify_bundle

        export = self._export()
        candidate = export / "controller_candidate"
        self.assertEqual(verify_export(export), {"series": 1, "chapters": 2, "pages": 3})
        accepted = verify_bundle(candidate)
        self.assertEqual({key: accepted[key] for key in ("series", "chapters", "pages")}, verify_export(export))
        self.assertFalse(accepted["rightsDeclared"])
        catalogue = json.loads((candidate / "catalogue.json").read_text(encoding="utf-8"))
        self.assertEqual([chapter["sequence"] for chapter in catalogue[0]["chapters"]], [0, 1])
        for chapter in catalogue[0]["chapters"]:
            manifest = json.loads(
                (candidate / "manifests" / f"{chapter['id']}.json").read_text(encoding="utf-8")
            )
            for page in manifest["pages"]:
                original = (candidate / "assets" / page["assetPath"]).read_bytes()
                checksum = hashlib.sha256(original).hexdigest()
                self.assertEqual(checksum, page["sha256"])
                self.assertEqual(
                    page["id"],
                    "pg_" + hashlib.sha256(f"{chapter['id']}:{checksum}".encode("ascii")).hexdigest()[:24],
                )

        first_ids = json.loads(self.registry.read_text(encoding="utf-8"))
        second = self._export("repeat")
        self.assertEqual(json.loads(self.registry.read_text(encoding="utf-8")), first_ids)
        self.assertEqual(verify_bundle(second / "controller_candidate")["pages"], 3)
        self.assertEqual(
            (candidate / "catalogue.json").read_bytes(),
            (second / "controller_candidate" / "catalogue.json").read_bytes(),
        )

    def test_both_validators_reject_changed_original_bytes(self) -> None:
        from taiyou_manga.builder import verify_bundle
        from taiyou_manga.domain import ControllerError

        export = self._export()
        candidate = export / "controller_candidate"
        original_page = next((candidate / "assets").rglob("*.png"))
        original_page.write_bytes(original_png((123, 100, 90)))
        with self.assertRaises(ImportFailure):
            verify_export(export)
        with self.assertRaises(ControllerError):
            verify_bundle(candidate)

    def test_controller_rejects_orphaned_asset(self) -> None:
        from taiyou_manga.builder import verify_bundle
        from taiyou_manga.domain import ControllerError

        export = self._export()
        candidate = export / "controller_candidate"
        (candidate / "assets" / "unexpected.txt").write_text("not a page", encoding="utf-8")
        with self.assertRaises(ControllerError):
            verify_bundle(candidate)


    def test_revision_guarded_local_mock_write_and_readback(self) -> None:
        """End-to-end simulation, explicitly isolated from all private HF datasets."""
        from taiyou_manga.builder import verify_bundle
        from taiyou_manga.domain import ControllerError
        from taiyou_manga.storage import MockStorage, RevisionConflict

        export = self._export()
        candidate = export / "controller_candidate"
        storage = MockStorage(self.root / "disposable-mock")
        plan = storage.preview(candidate)
        self.assertEqual(plan.status, "new")
        self.assertEqual(plan.new_pages, 3)
        self.assertIsNone(plan.revision)
        with self.assertRaises(ControllerError):
            storage.apply(candidate, expected_revision=plan.revision, approve=False)
        revision = storage.apply(candidate, expected_revision=plan.revision, approve=True)
        self.assertEqual(storage.health()["revision"], revision)
        snapshot = storage.root / "snapshots" / revision
        self.assertEqual(verify_bundle(snapshot)["pages"], 3)
        self.assertEqual(
            (candidate / "catalogue.json").read_bytes(),
            (snapshot / "catalogue.json").read_bytes(),
        )
        self.assertEqual(storage.preview(candidate).status, "no-op")
        with self.assertRaises(RevisionConflict):
            storage.apply(candidate, expected_revision="0" * 64, approve=True)

    def test_rights_declaration_is_not_proof_of_redistribution_rights(self) -> None:
        from taiyou_manga.builder import verify_bundle

        rights = self.root / "private-rights.json"
        rights.write_text(
            json.dumps({
                "schemaVersion": 1,
                "sourceType": "original",
                "title": "Synthetic Original",
                "permissionEvidence": "Entirely generated in this test",
                "attribution": "Synthetic integration test",
                "recordedAt": "2026-11-24T00:00:00Z",
            }),
            encoding="utf-8",
        )
        export = self._export(rights_path=rights)
        result = verify_bundle(export / "controller_candidate")
        self.assertTrue(result["rightsDeclared"])
        inventory = json.loads((export / "controller_candidate" / "inventory.json").read_text(encoding="utf-8"))
        self.assertTrue(inventory["rightsVerified"])


if __name__ == "__main__":
    unittest.main()
