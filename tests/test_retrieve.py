"""Synthetic Windows download orchestration, SHA verification and safe local export bundling."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from manga_retriever.retrieve import (
    RetrievalError,
    bundle_verified,
    choose_receipts,
    retrieve_one,
    retrieve_registered,
)

NOW = datetime(2026, 11, 19, tzinfo=UTC)


def make_export(path: Path) -> str:
    (path / "chapters").mkdir(parents=True)
    cbz = path / "chapters" / "ch_fake123456.cbz"
    with zipfile.ZipFile(cbz, "w") as archive:
        archive.writestr("0001.jpg", b"synthetic test bytes")
    (path / "download_manifest.json").write_text(json.dumps({"licensedSource": {
        "provider": "peppercarrot", "episode": 26, "licence": "CC BY 4.0"
    }}))
    (path / "controller_candidate").mkdir()
    (path / "controller_candidate" / "inventory.json").write_text("{\"sample\": true}")
    return hashlib.sha256(cbz.read_bytes()).hexdigest()


def receipt(digest: str, *, run: int = 1234, artifact: int = 4567,
            expires: str = "2099-11-26T00:00:00Z") -> dict:
    return {
        "schemaVersion": 1, "key": "peppercarrot:26", "provider": "peppercarrot", "episode": 26,
        "title": "Pepper&Carrot Episode 26: Books Are Great", "licence": "CC BY 4.0",
        "runId": run, "artifactId": artifact,
        "artifactUrl": f"https://github.com/RichardDaffern/Manga-Retriever/actions/runs/{run}/artifacts/{artifact}",
        "completedAt": "2026-11-19T00:00:00Z", "expiresAt": expires,
        "chapters": 1, "pages": 6, "sha256": digest,
    }


class RetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source"
        self.digest = make_export(self.source)
        self.record = receipt(self.digest)
        self.registry = self.root / "downloaded_manga.json"
        self.registry.write_text(json.dumps({"schemaVersion": 1, "downloads": [self.record]}))
        self.output = self.root / "downloads" / "peppercarrot-26-run-1234"
        self.commands = []

    def runner(self, command, *, check, timeout) -> None:
        self.commands.append((command, check, timeout))
        self.assertEqual(command[:4], ["gh", "run", "download", "1234"])
        self.assertEqual(command[4:6], ["--repo", "RichardDaffern/Manga-Retriever"])
        self.assertEqual(command[6:8], ["--name", "licensed-manga-1234-peppercarrot-26"])
        shutil.copytree(self.source, Path(command[-1]), dirs_exist_ok=True)

    @staticmethod
    def verifier(_path: Path) -> dict:
        return {"series": 1, "chapters": 1, "pages": 6}

    def test_choose_latest_unexpired(self) -> None:
        self.assertEqual(choose_receipts(self.registry, now=NOW)[0]["runId"], 1234)
        self.assertEqual(choose_receipts(self.registry, key="peppercarrot:26", run_id=1234, now=NOW)[0]["artifactId"], 4567)

    def test_download_and_skip_verified(self) -> None:
        result = retrieve_registered(self.registry, self.root / "downloads", runner=self.runner, verifier=self.verifier)
        self.assertEqual(result, {"peppercarrot:26": "downloaded-verified"})
        self.assertTrue(self.output.is_dir())
        result = retrieve_registered(self.registry, self.root / "downloads", runner=self.runner, verifier=self.verifier)
        self.assertEqual(result, {"peppercarrot:26": "skipped-verified"})
        self.assertEqual(len(self.commands), 1)

    def test_corrupt_existing_never_silently_skipped(self) -> None:
        shutil.copytree(self.source, self.output)
        next((self.output / "chapters").glob("*.cbz")).write_bytes(b"broken")
        with self.assertRaisesRegex(RetrievalError, "checksum"):
            retrieve_one(self.record, self.output, runner=self.runner, verifier=self.verifier)
        self.assertFalse(self.commands)

    def test_reject_unapproved_receipt_before_network(self) -> None:
        record = dict(self.record)
        record["key"] = "evil:1"
        with self.assertRaises(RetrievalError):
            retrieve_one(record, self.output, runner=self.runner, verifier=self.verifier)
        self.assertEqual(self.commands, [])

    def test_download_wrong_digest_remains_unpublished(self) -> None:
        record = dict(self.record)
        record["sha256"] = "a" * 64
        with self.assertRaisesRegex(RetrievalError, "checksum"):
            retrieve_one(record, self.output, runner=self.runner, verifier=self.verifier)
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.output.parent.glob(".manga-gh-retrieve-*")))

    def test_bad_run_does_not_replace_existing_files(self) -> None:
        self.output.parent.mkdir()
        self.output.write_text("existing unrelated output")
        with self.assertRaises(RetrievalError):
            retrieve_one(self.record, self.output, runner=self.runner, verifier=self.verifier)
        self.assertEqual(self.output.read_text(), "existing unrelated output")

    def test_failed_github_cli_leaves_no_partial_export(self) -> None:
        def fails(*args, **kwargs):
            raise subprocess.CalledProcessError(1, "gh")
        with self.assertRaisesRegex(RetrievalError, "GitHub CLI"):
            retrieve_one(self.record, self.output, runner=fails, verifier=self.verifier)
        self.assertFalse(self.output.exists())

    def test_reject_expired_and_unknown_sources(self) -> None:
        past = receipt(self.digest, expires="2026-11-18T00:00:00Z")
        past["completedAt"] = "2026-11-11T00:00:00Z"
        self.registry.write_text(json.dumps({"schemaVersion": 1, "downloads": [past]}))
        with self.assertRaisesRegex(RetrievalError, "unexpired"):
            choose_receipts(self.registry, now=NOW)
        with self.assertRaises(RetrievalError):
            choose_receipts(self.registry, key="evil:3", now=NOW)

    def test_bundle_verified_exports_preserves_bytes(self) -> None:
        folder = self.root / "ready"
        shutil.copytree(self.source, folder / "peppercarrot-26-run-1234")
        other = folder / "peppercarrot-26-run-1235"
        shutil.copytree(self.source, other)
        out = self.root / "complete.zip"
        counts = bundle_verified(folder, out, verifier=self.verifier)
        self.assertEqual(counts["exports"], 2)
        with zipfile.ZipFile(out) as archive:
            names = archive.namelist()
            self.assertIn("manga_bundle_manifest.json", names)
            manifest = json.loads(archive.read("manga_bundle_manifest.json"))
            self.assertEqual(manifest["schemaVersion"], 1)
            self.assertEqual(len(manifest["exports"]), 2)
            for member, digest in manifest["files"].items():
                self.assertEqual(hashlib.sha256(archive.read(member)).hexdigest(), digest)
        with self.assertRaisesRegex(RetrievalError, "output must be new"):
            bundle_verified(folder, out, verifier=self.verifier)

    def test_bundle_rejects_symlinks_and_nested_output(self) -> None:
        folder = self.root / "ready"
        shutil.copytree(self.source, folder / "one")
        with self.assertRaisesRegex(RetrievalError, "inside source"):
            bundle_verified(folder, folder / "bundle.zip", verifier=self.verifier)
        try:
            (folder / "one" / "evil").symlink_to(self.registry)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks disabled on this Windows test runner")
        with self.assertRaisesRegex(RetrievalError, "Symlinks"):
            bundle_verified(folder, self.root / "outside.zip", verifier=self.verifier)

    def test_refuse_archive_of_unverified_export(self) -> None:
        folder = self.root / "ready"
        shutil.copytree(self.source, folder / "unverified")
        def fails(path):
            raise RetrievalError("invalid export")
        with self.assertRaisesRegex(RetrievalError, "invalid export"):
            bundle_verified(folder, self.root / "output.zip", verifier=fails)
        self.assertFalse((self.root / "output.zip").exists())


if __name__ == "__main__":
    unittest.main()
