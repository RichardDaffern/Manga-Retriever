"""Offline, zero-network verification of six-title historical artifact recovery."""
from __future__ import annotations

import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from scripts.recover_existing_manga import (
    RecoveryError,
    _audit_files,
    _safe_extract,
    load_manifest,
    audit_availability,
    recover_all,
    recover_one,
)


def _jpeg_bytes() -> bytes:
    image = Image.effect_noise((390, 530), 70).convert("RGB")
    stream = io.BytesIO()
    image.save(stream, "JPEG", quality=95)
    return stream.getvalue()


def _outer_artifact() -> bytes:
    cbz = io.BytesIO()
    with zipfile.ZipFile(cbz, "w") as z:
        z.writestr("001.jpg", _jpeg_bytes(), compress_type=zipfile.ZIP_STORED)
    outer = io.BytesIO()
    with zipfile.ZipFile(outer, "w") as z:
        z.writestr("example/chapters/Vol. 1 Ch. 1.cbz",
                   cbz.getvalue(), compress_type=zipfile.ZIP_STORED)
        z.writestr("example/quality_audit.json",
                   json.dumps({"verifiedArchives": 1, "verifiedPages": 1}))
    return outer.getvalue()


class HistoricalArtifactRecoveryTests(unittest.TestCase):
    def test_inventory_contains_distinct_real_artifact_ids(self):
        data = load_manifest()
        self.assertEqual(set(data["titles"]), {
            "relife", "love-so-life", "last-game", "maid-sama",
            "onizuka-sawarida", "kainushi-wa-akuma",
        })
        ids = [v["artifactId"] for s in data["titles"].values() for v in s["items"]]
        self.assertEqual(len(ids), 33)
        self.assertEqual(len(ids), len(set(ids)))

    def test_zip_is_safely_extracted_and_real_image_bytes_verified(self):
        with tempfile.TemporaryDirectory() as home:
            archive = Path(home) / "download.zip"
            archive.write_bytes(_outer_artifact())
            out = Path(home) / "unpacked"
            out.mkdir()
            _safe_extract(archive, out)
            report = _audit_files(out)
            self.assertEqual(report["verifiedCBZ"], 1)
            self.assertEqual(report["verifiedPages"], 1)
            self.assertEqual(len(report["archives"][0]["sha256"]), 64)

    def test_zip_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as home:
            archive = Path(home) / "unsafe.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("../outside.txt", b"unsafe")
            with self.assertRaisesRegex(RecoveryError, "traversal"):
                _safe_extract(archive, Path(home))

    def test_altered_source_audit_rejected(self):
        with tempfile.TemporaryDirectory() as home:
            folder = Path(home) / "media"
            folder.mkdir()
            archive = Path(home) / "data.zip"
            archive.write_bytes(_outer_artifact())
            _safe_extract(archive, folder)
            quality = folder / "example/quality_audit.json"
            quality.write_text('{"verifiedArchives":1,"verifiedPages":500}')
            with self.assertRaisesRegex(RecoveryError, "image count mismatch"):
                _audit_files(folder)

    def test_real_zip_source_download_and_skip_existing_are_safe(self):
        manifest = load_manifest()
        item = manifest["titles"]["onizuka-sawarida"]["items"][0]
        bytes_ = _outer_artifact()
        calls = []

        def runner(argv, **kwargs):
            calls.append(argv)
            if argv[-1].endswith("/zip"):
                kwargs["stdout"].write(bytes_)
                return subprocess.CompletedProcess(argv, 0, b"", b"")
            return subprocess.CompletedProcess(argv, 0, json.dumps({
                "id": item["artifactId"], "name": item["name"],
                "expired": False, "size_in_bytes": len(bytes_),
                "workflow_run": {"id": item["runId"]},
                "expires_at": "2026-11-27T04:39:35Z",
            }), "")

        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            result = recover_one("onizuka-sawarida", item, root, runner=runner)
            self.assertEqual(result["outcome"], "downloaded-and-verified")
            self.assertEqual(result["verifiedCBZ"], 1)
            self.assertEqual(result["verifiedPages"], 1)
            self.assertTrue((root / "onizuka-sawarida" / item["name"] /
                             "recovery-verification.json").exists())
            calls_before = len(calls)
            resumed = recover_one("onizuka-sawarida", item, root, runner=runner)
            self.assertEqual(resumed["outcome"], "already-verified")
            self.assertEqual(len(calls), calls_before)

    def test_wrong_github_artifact_id_refused_without_output(self):
        item = load_manifest()["titles"]["relife"]["items"][0]

        def runner(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 0, json.dumps({
                "id": 1, "name": item["name"], "expired": False,
                "workflow_run": {"id": item["runId"]},
            }), "")

        with tempfile.TemporaryDirectory() as home:
            with self.assertRaisesRegex(RecoveryError, "identity mismatch"):
                recover_one("relife", item, Path(home), runner=runner)
            self.assertFalse((Path(home) / "relife" / item["name"]).exists())

    def test_parallel_errors_do_not_hide_other_verified_artifacts(self):
        manifest = {"titles": {
            "one": {"items": [{"artifactId": 1, "name": "a", "runId": 4, "range": "1-2"}]},
            "two": {"items": [{"artifactId": 2, "name": "b", "runId": 5, "range": "3-4"}]},
        }}
        def fake_recover(slug, item, root, **kwargs):
            if slug == "one":
                raise RecoveryError("Simulated expired artifact")
            return {"outcome": "downloaded-and-verified", "verifiedCBZ": 2,
                    "verifiedPages": 39}

        with tempfile.TemporaryDirectory() as home:
            with patch("scripts.recover_existing_manga.recover_one", fake_recover):
                report = recover_all(["one", "two"], Path(home), manifest=manifest)
            self.assertEqual(report["status"], "partial")
            self.assertEqual(report["verifiedArtifacts"], 1)
            self.assertEqual(report["verifiedImages"], 39)
            self.assertTrue((Path(home) / "historical-recovery-status.json").exists())


    def test_read_only_availability_preflight_never_fetches_zip(self):
        item = load_manifest()["titles"]["onizuka-sawarida"]["items"][0]
        manifest = {"titles": {"one": {"items": [item]}}}
        called = []

        def runner(argv, **kwargs):
            called.append(argv[-1])
            return subprocess.CompletedProcess(argv, 0, json.dumps({
                "id": item["artifactId"],
                "name": item["name"],
                "expired": False,
                "expires_at": "2026-11-27T04:39:35Z",
                "size_in_bytes": 29052583,
                "workflow_run": {"id": item["runId"]},
            }), "")

        with tempfile.TemporaryDirectory() as home:
            report = audit_availability(["one"], Path(home), runner=runner, manifest=manifest)
            self.assertEqual(report["status"], "recoverable-or-retained")
            self.assertEqual(report["unexpired"], 1)
            self.assertEqual(report["verifiedLocal"], 0)
            self.assertEqual(report["results"][0]["localState"], "missing-local")
            self.assertFalse(report["mediaDownloaded"])
            self.assertEqual(len(called), 1)
            self.assertNotIn("/zip", called[0])
            self.assertEqual(list(Path(home).iterdir()), [])

    def test_read_only_preflight_accepts_verified_local_copy_after_expiry(self):
        item = load_manifest()["titles"]["onizuka-sawarida"]["items"][0]
        manifest = {"titles": {"one": {"items": [item]}}}
        data = _outer_artifact()

        def runner(argv, **kwargs):
            if argv[-1].endswith("/zip"):
                kwargs["stdout"].write(data)
                return subprocess.CompletedProcess(argv, 0, b"", b"")
            return subprocess.CompletedProcess(argv, 0, json.dumps({
                "id": item["artifactId"], "name": item["name"],
                "expired": False, "size_in_bytes": len(data),
                "workflow_run": {"id": item["runId"]},
            }), "")

        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            recover_one("one", item, root, runner=runner)

            def expired_runner(argv, **kwargs):
                return subprocess.CompletedProcess(argv, 0, json.dumps({
                    "id": item["artifactId"], "name": item["name"],
                    "expired": True,
                    "workflow_run": {"id": item["runId"]},
                }), "")

            report = audit_availability(["one"], root, runner=expired_runner, manifest=manifest)
            self.assertEqual(report["status"], "recoverable-or-retained")
            self.assertEqual(report["verifiedLocal"], 1)
            self.assertEqual(report["unexpired"], 0)
            self.assertEqual(report["attentionRequired"], 0)

    def test_read_only_preflight_flags_unverified_missing_archive(self):
        item = load_manifest()["titles"]["relife"]["items"][0]
        manifest = {"titles": {"one": {"items": [item]}}}

        def expired_runner(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 0, json.dumps({
                "id": item["artifactId"], "name": item["name"], "expired": True,
                "workflow_run": {"id": item["runId"]},
            }), "")

        result = audit_availability(["one"], runner=expired_runner, manifest=manifest)
        self.assertEqual(result["status"], "attention-required")
        self.assertEqual(result["attentionRequired"], 1)
        self.assertEqual(result["results"][0]["remoteState"], "expired")


if __name__ == "__main__":
    unittest.main()
