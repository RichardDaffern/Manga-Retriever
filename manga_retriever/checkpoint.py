"""Restart-safe, bounded page checkpoints for explicitly approved acquisitions.

No remote media is published here. Callers validate licence and approved URLs
before creating the page plan; each page is independently verified and fsynced.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections.abc import Callable, Iterable
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class CheckpointError(ValueError):
    """Invalid checkpoint, concurrent write, or incompatible source plan."""


@dataclass(frozen=True)
class PageSpec:
    number: int
    url: str
    suffix: str = ".jpg"

    @property
    def filename(self) -> str:
        return f"{self.number:04d}{self.suffix}"


def _write_atomic(path: Path, data: bytes) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=".manga-write-", suffix=".tmp", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def _exclusive_lock(path: Path):
    if path.is_symlink() or path.parent.is_symlink():
        raise CheckpointError("Checkpoint lock path is a symlink")
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise CheckpointError("Checkpoint is in use; inspect a stale lock before retrying") from exc
    try:
        os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)


class PageCheckpoint:
    """Complete page plan with atomic per-page progress and bounded reuse.

    Only the exact declared page plan may be resumed. A cached page is reused
    after recomputing its checksum and fully validating its contents; an invalid
    cached page is fetched again, never treated as completed.
    """

    VERSION = 1

    def __init__(
        self,
        directory: Path,
        source: str,
        pages: Iterable[PageSpec],
        *,
        maximum_bytes: int,
        validate: Callable[[bytes, str], Any],
    ) -> None:
        self.directory = Path(directory)
        self.source = source
        self.pages = tuple(pages)
        self.maximum_bytes = maximum_bytes
        self.validate = validate
        if (
            not self.pages
            or len(self.pages) > 1000
            or len({page.number for page in self.pages}) != len(self.pages)
            or [page.number for page in self.pages] != sorted(page.number for page in self.pages)
            or any(page.number < 1 or page.number > 9999 for page in self.pages)
            or any(page.suffix not in {".png", ".jpg", ".jpeg", ".webp", ".avif"} for page in self.pages)
            or any(not page.url.startswith("https://") or len(page.url) > 2048 for page in self.pages)
            or not source.startswith("https://")
            or not 1 <= maximum_bytes <= 25_000_000
        ):
            raise CheckpointError("Invalid bounded checkpoint plan")

    @property
    def page_folder(self) -> Path:
        return self.directory / "pages"

    @property
    def index_path(self) -> Path:
        return self.directory / "checkpoint.json"

    def _plan(self) -> list[dict[str, object]]:
        return [{"number": page.number, "url": page.url, "filename": page.filename} for page in self.pages]

    def _load(self) -> dict[str, Any]:
        if self.index_path.is_symlink():
            raise CheckpointError("Checkpoint index is a symlink")
        if not self.index_path.exists():
            if any(self.directory.iterdir()):
                # It is valid for an empty pages/ directory to exist, but not
                # orphaned files or an unowned source manifest.
                others = [p for p in self.directory.iterdir() if p != self.page_folder]
                if others or (self.page_folder.exists() and any(self.page_folder.iterdir())):
                    raise CheckpointError("Unindexed checkpoint files; refusing unsafe reuse")
            return {"schemaVersion": self.VERSION, "source": self.source, "plan": self._plan(), "completed": {}}
        try:
            state = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise CheckpointError("Cannot decode checkpoint index") from exc
        if (
            not isinstance(state, dict)
            or set(state) != {"schemaVersion", "source", "plan", "completed"}
            or state["schemaVersion"] != self.VERSION
            or state["source"] != self.source
            or state["plan"] != self._plan()
            or not isinstance(state["completed"], dict)
        ):
            raise CheckpointError("Checkpoint schema or source plan changed")
        expected = {page.filename for page in self.pages}
        if not set(state["completed"]).issubset(expected):
            raise CheckpointError("Unknown page in checkpoint index")
        for metadata in state["completed"].values():
            if (
                not isinstance(metadata, dict)
                or set(metadata) != {"sha256", "byteSize"}
                or not isinstance(metadata["sha256"], str)
                or not re.fullmatch("[a-f0-9]{64}", metadata["sha256"])
                or type(metadata["byteSize"]) is not int
                or not 1 <= metadata["byteSize"] <= self.maximum_bytes
            ):
                raise CheckpointError("Invalid completed page metadata")
        return state

    def _persist(self, state: dict[str, Any]) -> None:
        data = (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8")
        _write_atomic(self.index_path, data)

    def _check_cached(self, path: Path, metadata: dict[str, Any] | None) -> bool:
        if metadata is None or not path.is_file() or path.is_symlink():
            return False
        if path.stat().st_size != metadata["byteSize"]:
            return False
        with path.open("rb") as reader:
            data = reader.read(self.maximum_bytes + 1)
        if len(data) != metadata["byteSize"] or hashlib.sha256(data).hexdigest() != metadata["sha256"]:
            return False
        try:
            self.validate(data, path.name)
        except (ValueError, OSError, SyntaxError):
            return False
        return True

    def run(self, fetch: Callable[[str, int], bytes]) -> dict[str, int]:
        if self.directory.is_symlink() or self.page_folder.is_symlink():
            raise CheckpointError("Checkpoint directory is a symlink")
        self.directory.parent.mkdir(parents=True, exist_ok=True)
        with _exclusive_lock(self.directory.with_name(self.directory.name + ".lock")):
            self.directory.mkdir(exist_ok=True)
            self.page_folder.mkdir(exist_ok=True)
            state = self._load()
            expected_files = {page.filename for page in self.pages}
            for entry in self.page_folder.iterdir():
                if entry.name not in expected_files or entry.is_symlink() or not entry.is_file():
                    raise CheckpointError("Unexpected checkpoint page file")
            if not self.index_path.exists():
                self._persist(state)
            reused = 0
            retrieved = 0
            for page in self.pages:
                path = self.page_folder / page.filename
                metadata = state["completed"].get(page.filename)
                if self._check_cached(path, metadata):
                    reused += 1
                    continue
                data = fetch(page.url, self.maximum_bytes)
                if not isinstance(data, bytes) or not 1 <= len(data) <= self.maximum_bytes:
                    raise CheckpointError("Downloaded page is empty or over the limit")
                self.validate(data, page.filename)
                _write_atomic(path, data)
                state["completed"][page.filename] = {
                    "sha256": hashlib.sha256(data).hexdigest(), "byteSize": len(data)
                }
                self._persist(state)
                retrieved += 1
            return {"reused": reused, "downloaded": retrieved, "pages": len(self.pages)}
