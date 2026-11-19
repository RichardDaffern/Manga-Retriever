"""Synthetic allowlist, artifact registry and partial-batch recovery tests."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from manga_retriever.batch import (
    BatchError,
    consolidate,
    main,
    parse_matrix,
    parse_selection,
    receipt_from_export,
    validate_receipt,
)
from manga_retriever.peppercarrot import LICENCE_URL, SOURCE_PAGE


NOW = datetime(2026, 11, 19, tzinfo=UTC)
RUN = 7654321
ARTIFACT = 123456
URL = (
    f"https://github.com/RichardDaffern/Manga-Retriever/actions/runs/{RUN}/artifacts/{ARTIFACT}"
)
SOURCE_ROOT = (
    "https://www.peppercarrot.com/0_sources/ep26_Books-Are-Great/hi-res/"
    "en_Pepper-and-Carrot_by-David-Revoy_E26P"
)


def receipt() -> dict:
    return {
        "schemaVersion": 1,
        "key": "peppercarrot:26",
        "provider": "peppercarrot",
        "episode": 26,
        "title": "Pepper&Carrot Episode 26: Books Are Great",
        "licence": "CC BY 4.0",
        "runId": RUN,
        "artifactId": ARTIFACT,
        "artifactUrl": URL,
        "completedAt": "2026-11-19T00:00:00Z",
        "expiresAt": "2026-11-26T00:00:00Z",
        "chapters": 1,
        "pages": 6,
        "sha256": "a" * 64,
    }


class BatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.receipts = self.root / "receipts"
        self.receipts.mkdir()
        self.registry = self.root / "downloaded_manga.json"
        self.md = self.root / "DOWNLOADED_MANGA.md"
        self.status = self.root / "status.json"

    def test_parse_whitelist(self) -> None:
        self.assertEqual(parse_selection(" peppercarrot:26 "), ["peppercarrot:26"])
        self.assertEqual(parse_matrix('[{"key":"peppercarrot:26","slug":"peppercarrot-26"}]'), ["peppercarrot:26"])

    def test_no_arbitrary_url_or_unapproved_series(self) -> None:
        for item in ("https://example.com/other.jpg", "peppercarrot:27", "../path", " ", "a" * 513):
            with self.subTest(item=item[:30]), self.assertRaises(BatchError):
                parse_selection(item)

    def test_duplicate_rejected(self) -> None:
        with self.assertRaises(BatchError):
            parse_selection("peppercarrot:26,peppercarrot:26")

    def test_bad_matrix_slug_rejected(self) -> None:
        with self.assertRaises(BatchError):
            parse_matrix('[{"key":"peppercarrot:26","slug":"../../etc/passwd"}]')

    def test_receipt_validation(self) -> None:
        self.assertEqual(validate_receipt(receipt()), receipt())
        for field, val in (("artifactUrl", "https://evil.test"), ("licence", "none"),
                           ("sha256", "abcd"), ("pages", 5), ("schemaVersion", 2),
                           ("artifactId", True), ("provider", "other"), ("key", "other:3")):
            value = receipt()
            value[field] = val
            with self.subTest(field=field), self.assertRaises(BatchError):
                validate_receipt(value)

    def test_bad_expiry_rejected(self) -> None:
        val = receipt()
        val["expiresAt"] = "2026-11-10T00:00:00Z"
        with self.assertRaises(BatchError):
            validate_receipt(val)

    def test_consolidate_complete_and_idempotent(self) -> None:
        (self.receipts / "record.json").write_text(json.dumps(receipt()))
        expected = ["peppercarrot:26"]
        self.assertEqual(consolidate(self.receipts, expected, self.registry, self.md, self.status)["missing"], [])
        self.assertEqual(consolidate(self.receipts, expected, self.registry, self.md, self.status)["missing"], [])
        actual = json.loads(self.registry.read_text())
        self.assertEqual(actual["schemaVersion"], 1)
        self.assertEqual(len(actual["downloads"]), 1)
        self.assertIn("Run 7654321", self.md.read_text())
        self.assertNotIn("manga/mng_", self.md.read_text())

    def test_partial_batch_writes_missing_plan(self) -> None:
        status = consolidate(self.receipts, ["peppercarrot:26"], self.registry, self.md, self.status)
        self.assertEqual(status["missing"], ["peppercarrot:26"])
        self.assertTrue(self.registry.exists())
        self.assertEqual(json.loads(self.registry.read_text())["downloads"], [])
        self.assertEqual(main(["check-status", "--status", str(self.status)]), 1)

    def test_invalid_receipt_does_not_touch_registry(self) -> None:
        val = receipt()
        val["artifactUrl"] = "https://evil.test/phishing"
        (self.receipts / "bad.json").write_text(json.dumps(val))
        with self.assertRaises(BatchError):
            consolidate(self.receipts, ["peppercarrot:26"], self.registry, self.md, self.status)
        self.assertFalse(self.registry.exists())

    def test_duplicate_receipts_rejected(self) -> None:
        (self.receipts / "first.json").write_text(json.dumps(receipt()))
        (self.receipts / "second.json").write_text(json.dumps(receipt()))
        with self.assertRaises(BatchError):
            consolidate(self.receipts, ["peppercarrot:26"], self.registry, self.md, self.status)

    def test_future_registry_version_fails_closed(self) -> None:
        self.registry.write_text('{"schemaVersion":2,"downloads":[]}')
        with self.assertRaises(BatchError):
            consolidate(self.receipts, ["peppercarrot:26"], self.registry, self.md, self.status)

    def test_prepare_github_output(self) -> None:
        out = self.root / "github-out.txt"
        with patch.dict(os.environ, {"GITHUB_OUTPUT": str(out)}):
            self.assertEqual(main(["prepare", "--selection", "peppercarrot:26"]), 0)
        self.assertIn('jobs=[{"key":"peppercarrot:26","slug":"peppercarrot-26"}]', out.read_text())

    def test_verified_export_produces_short_lived_metadata_receipt(self) -> None:
        export = self.root / "export"
        (export / "chapters").mkdir(parents=True)
        with zipfile.ZipFile(export / "chapters" / "ch_test12345.cbz", "w") as writer:
            writer.writestr("0001.jpg", b"synthetic pages, not used for image verification")
        pages = [
            {
                "pageNumber": n,
                "sourceUrl": f"{SOURCE_ROOT}{n:02d}.jpg",
                "assetPath": f"manga/opaque/opaque/p{n}.jpg",
                "sha256": hashlib.sha256(str(n).encode()).hexdigest(),
            }
            for n in range(1, 7)
        ]
        (export / "download_manifest.json").write_text(json.dumps({"licensedSource": {
            "provider": "peppercarrot", "episode": 26, "licence": "CC BY 4.0", "sourcePage": SOURCE_PAGE,
            "licenceUrl": LICENCE_URL, "pages": pages,
        }}))
        value = receipt_from_export(
            "peppercarrot:26", export, RUN, ARTIFACT, URL, now=NOW,
            verifier=lambda path: {"series": 1, "chapters": 1, "pages": 6},
        )
        self.assertEqual(value["expiresAt"], "2026-11-26T00:00:00Z")
        self.assertTrue(value["sha256"])
        validate_receipt(value)
        with self.assertRaises(BatchError):
            receipt_from_export(
                "peppercarrot:26", export, RUN, ARTIFACT, URL, now=NOW,
                verifier=lambda path: {"series": 1, "chapters": 1, "pages": 5},
            )


if __name__ == "__main__":
    unittest.main()
