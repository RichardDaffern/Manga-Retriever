"""Typed, side-effect-explicit source acquisition port.

Adapters output the same verified export; they never upload or mutate readers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from .importer import import_local
from .peppercarrot import download_episode_26


@runtime_checkable
class MangaSourceAdapter(Protocol):
    source_id: str

    def acquire(self, output: Path, registry: Path) -> dict[str, int]: ...


@dataclass(frozen=True)
class LocalImportAdapter:
    source: Path
    direction: str = "rtl"
    rights_path: Path | None = None
    source_id: str = "local"

    def acquire(self, output: Path, registry: Path) -> dict[str, int]:
        return import_local(self.source, output, registry, rights_path=self.rights_path,
                            direction=self.direction)


@dataclass(frozen=True)
class PepperCarrotEpisode26Adapter:
    source_id: str = "peppercarrot"

    def acquire(self, output: Path, registry: Path) -> dict[str, int]:
        return download_episode_26(output, registry)
