"""Resumable checkpoint regression suite with synthetic, owned image bytes."""

from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from manga_retriever.checkpoint import CheckpointError, PageCheckpoint, PageSpec


def jpeg(index: int) -> bytes:
    stream = io.BytesIO()
    Image.new("RGB", (24, 18), (index * 30, 10, 70)).save(stream, format="JPEG")
    return stream.getvalue()


URL_ROOT = "https://example.invalid/licensed/page"


class CheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / "partial"
        self.pages = tuple(PageSpec(i, f"{URL_ROOT}{i}.jpg") for i in range(1, 4))
        self.payloads = {p.url: jpeg(p.number) for p in self.pages}
        self.requests: list[str] = []

    def checkpoint(self, pages=None):
        def validate(data: bytes, name: str) -> None:
            with Image.open(io.BytesIO(data)) as image:
                if image.format != "JPEG" or not name.endswith(".jpg"):
                    raise ValueError("Not JPEG")
                image.load()

        return PageCheckpoint(
            self.folder, "https://example.invalid/licensed", pages or self.pages,
            maximum_bytes=25000, validate=validate,
        )

    def fetch(self, url: str, max_bytes: int) -> bytes:
        self.requests.append(url)
        return self.payloads[url]

    def test_fresh_download_and_reuse(self) -> None:
        checkpoint = self.checkpoint()
        self.assertEqual(checkpoint.run(self.fetch), {"reused": 0, "downloaded": 3, "pages": 3})
        self.assertEqual(checkpoint.run(self.fetch), {"reused": 3, "downloaded": 0, "pages": 3})
        self.assertEqual(len(self.requests), 3)
        self.assertEqual(sorted(x.name for x in checkpoint.page_folder.iterdir()),
                         ["0001.jpg", "0002.jpg", "0003.jpg"])
        state = json.loads(checkpoint.index_path.read_text(encoding="utf-8"))
        self.assertEqual(state["schemaVersion"], 1)
        self.assertEqual(state["completed"]["0001.jpg"]["sha256"],
                         hashlib.sha256(self.payloads[self.pages[0].url]).hexdigest())

    def test_partial_failure_then_resume_only_missing(self) -> None:
        fail = True

        def intermittent(url: str, maximum: int) -> bytes:
            if url == self.pages[1].url and fail:
                raise ConnectionError("interrupted")
            return self.fetch(url, maximum)

        with self.assertRaises(ConnectionError):
            self.checkpoint().run(intermittent)
        self.assertEqual([p.name for p in self.checkpoint().page_folder.iterdir()], ["0001.jpg"])
        fail = False
        result = self.checkpoint().run(intermittent)
        self.assertEqual(result, {"reused": 1, "downloaded": 2, "pages": 3})
        self.assertEqual(self.requests.count(self.pages[0].url), 1)
        self.assertFalse((self.folder.with_name(self.folder.name + ".lock")).exists())

    def test_corrupt_cached_page_redownloaded(self) -> None:
        self.checkpoint().run(self.fetch)
        (self.folder / "pages" / "0002.jpg").write_bytes(b"corruption")
        self.requests.clear()
        self.assertEqual(self.checkpoint().run(self.fetch)["downloaded"], 1)
        self.assertEqual(self.requests, [self.pages[1].url])

    def test_corrupt_jpeg_never_checkpointed(self) -> None:
        self.payloads[self.pages[0].url] = b"junk"
        with self.assertRaises((ValueError, OSError, SyntaxError)):
            self.checkpoint().run(self.fetch)
        state = json.loads((self.folder / "checkpoint.json").read_text())
        self.assertEqual(state["completed"], {})
        self.assertFalse((self.folder / "pages" / "0001.jpg").exists())

    def test_source_plan_changed_rejected(self) -> None:
        self.checkpoint().run(self.fetch)
        changed = (PageSpec(1, "https://example.invalid/another"), *self.pages[1:])
        with self.assertRaisesRegex(CheckpointError, "plan changed"):
            self.checkpoint(changed).run(self.fetch)

    def test_source_version_changed_rejected(self) -> None:
        self.checkpoint().run(self.fetch)
        state_path = self.folder / "checkpoint.json"
        state = json.loads(state_path.read_text())
        state["schemaVersion"] = 3
        state_path.write_text(json.dumps(state))
        with self.assertRaises(CheckpointError):
            self.checkpoint().run(self.fetch)

    def test_unindexed_page_not_reused(self) -> None:
        self.folder.mkdir()
        (self.folder / "pages").mkdir()
        (self.folder / "pages" / "0001.jpg").write_bytes(jpeg(1))
        with self.assertRaises(CheckpointError):
            self.checkpoint().run(self.fetch)

    def test_unknown_page_file_rejected(self) -> None:
        self.checkpoint().run(self.fetch)
        (self.folder / "pages" / "0004.jpg").write_bytes(b"wrong")
        with self.assertRaises(CheckpointError):
            self.checkpoint().run(self.fetch)

    def test_concurrent_lock_rejected(self) -> None:
        lock = self.folder.with_name(self.folder.name + ".lock")
        lock.write_text("in use")
        with self.assertRaisesRegex(CheckpointError, "in use"):
            self.checkpoint().run(self.fetch)

    def test_oversized_page_not_persisted(self) -> None:
        def oversize(url: str, max_bytes: int) -> bytes:
            return b"x" * (max_bytes + 1)
        with self.assertRaises(CheckpointError):
            self.checkpoint().run(oversize)
        self.assertFalse((self.folder / "pages" / "0001.jpg").exists())

    def test_malformed_metadata_rejected(self) -> None:
        self.checkpoint().run(self.fetch)
        state_path = self.folder / "checkpoint.json"
        state = json.loads(state_path.read_text())
        state["completed"]["0001.jpg"]["byteSize"] = -1
        state_path.write_text(json.dumps(state))
        with self.assertRaises(CheckpointError):
            self.checkpoint().run(self.fetch)

    def test_symlink_index_rejected(self) -> None:
        self.folder.mkdir()
        (self.folder / "pages").mkdir()
        target = Path(self.temp.name) / "external.json"
        target.write_text("{}")
        try:
            (self.folder / "checkpoint.json").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Filesystem has no symlink permissions")
        with self.assertRaises(CheckpointError):
            self.checkpoint().run(self.fetch)
        self.assertEqual(target.read_text(), "{}")


if __name__ == "__main__":
    unittest.main()
