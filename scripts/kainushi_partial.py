"""Kainushi wa Akuma: bounded English MangaDex partial-set retriever.

Downloads only the manga's MangaDex-hosted English chapter labels, never
silently calls the series complete relative to other English indexes.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from manga_retriever.relife import ReLIFEError, _inspect_cbz, _safe_output
from scripts.love_kainushi_readiness import (
    KAINUSHI_EXTERNAL_LABELS,
    external_label_difference,
    labels_from_feed,
)
from scripts.source_probe_eight import MangaDexMetadata

MANGA_ID = "2f46b87a-00dd-4cd3-bf47-68126fb05793"
TITLE = "Kainushi wa Akuma"
RANGES = {1: (1, 10), 2: (10, 19), 3: (19, 26)}
FILENAME_LABEL = re.compile(r"\bch(?:apter)?\.?\s*(\d+(?:\.\d+)?)(?=\b|$)", re.IGNORECASE)


class PartialSourceError(ValueError):
    """A result cannot safely be downloaded or verified."""


def range_labels(source_labels: list[str], lower: int, upper: int) -> list[str]:
    if (lower, upper) not in RANGES.values():
        raise PartialSourceError("Only three fixed English source batches are allowed")
    return sorted(
        (label for label in source_labels if Decimal(lower) <= Decimal(label) < Decimal(upper)),
        key=lambda value: (Decimal(value), value),
    )


def chapter_filename_label(path: Path) -> str | None:
    match = FILENAME_LABEL.search(path.stem)
    return match.group(1) if match else None


def command(first_label: str, last_label: str, output: Path) -> list[str]:
    _safe_output(output)
    if not all(re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", x) for x in [first_label, last_label]):
        raise PartialSourceError("Invalid source chapter labels")
    return [
        sys.executable, "-m", "mangadex_downloader",
        "https://mangadex.org/title/" + MANGA_ID,
        "--language", "en", "--save-as", "cbz", "--path", str(output),
        "--start-chapter", first_label, "--end-chapter", last_label,
        "--order", "oldest", "--http-retries", "3", "--delay-requests", "2",
    ]


def inspect_and_stage(
    output: Path, verified_folder: Path, expected: list[str], *, client_return_code: int,
    source_labels: list[str],
) -> dict:
    _safe_output(output)
    _safe_output(verified_folder)
    if not output.is_dir():
        raise PartialSourceError("Downloaded source directory not found")
    if output.is_symlink() or any(entry.is_symlink() for entry in output.rglob("*")):
        raise PartialSourceError("Symlinks are not permitted in source output")
    if verified_folder.exists():
        raise PartialSourceError("Refusing to overwrite verified output")
    verified_folder.mkdir(parents=True)
    expected_set = set(expected)
    found: set[str] = set()
    warnings: list[str] = []
    records: list[dict] = []
    count = 0
    for cbz in sorted(output.rglob("*.cbz")):
        count += 1
        if count > 100:
            raise PartialSourceError("Too many downloaded archives in one batch")
        label = chapter_filename_label(cbz)
        if label is None or label not in expected_set or label in found:
            warnings.append(f"Unmatched/duplicate label (excluded): {cbz.name[:100]}")
            continue
        try:
            inspected = _inspect_cbz(cbz)
        except (ReLIFEError, OSError, ValueError):
            warnings.append(f"Corrupt/unverifiable chapter (excluded): {cbz.name[:100]}")
            continue
        relative = cbz.relative_to(output)
        dest = verified_folder / "chapters" / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cbz, dest)
        if _inspect_cbz(dest)["sha256"] != inspected["sha256"]:
            raise PartialSourceError("Copy integrity mismatch")
        inspected["chapterLabel"] = label
        inspected["relativePath"] = relative.as_posix()
        records.append(inspected)
        found.add(label)

    missing = sorted(expected_set - found, key=Decimal)
    total_pages = sum(record["verifiedPageCount"] for record in records)
    external = external_label_difference(source_labels, KAINUSHI_EXTERNAL_LABELS)
    report = {
        "schemaVersion": 1,
        "title": TITLE,
        "sourceTitleId": MANGA_ID,
        "source": "MangaDex English scanlation uploads, uploader-original quality requested",
        "sourceInventoryEnglishChapterLabels": len(source_labels),
        "sourceVsExternalCatalogue": external,
        "requestedLabels": expected,
        "verifiedLabels": sorted(found, key=Decimal),
        "missingLabelsWithinRequestedBatch": missing,
        "verifiedCBZCount": len(records),
        "verifiedImagePages": total_pages,
        "clientExitCode": client_return_code,
        "warnings": warnings,
        "completeAgainstMangaDexRequestedBatch": not missing and client_return_code == 0,
        "completeOriginalManga": False,
        "notes": "The 56-item external chapter index includes labels absent on MangaDex. A CBZ audit cannot prove publisher master-quality images or content licensing.",
        "createdAtUtc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archives": records,
    }
    (verified_folder / "quality_audit.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (verified_folder / "SOURCE_AND_RIGHTS.txt").write_text(
        "Kainushi wa Akuma, Eiri Kaji. English source: MangaDex.\n"
        "https://mangadex.org/title/" + MANGA_ID + "\n"
        "Credit MangaDex and the applicable English scanlation groups.\n"
        "Partial English source inventory; absent labels are reported in quality_audit.json.\n"
        "Access does not establish redistribution or publisher-master rights.\n",
        encoding="utf-8",
    )
    return report


def run_batch(batch: int, output: Path, verified_output: Path, *, client=None, runner=subprocess.run,
              module_exists=importlib.util.find_spec) -> dict:
    if batch not in RANGES:
        raise PartialSourceError("Unapproved batch")
    if module_exists("mangadex_downloader") is None:
        raise PartialSourceError("Install pinned mangadex-downloader==3.1.4")
    lower, upper = RANGES[batch]
    client = client or MangaDexMetadata(delay=2)
    total, chapters = client.feed(MANGA_ID)
    if total != len(chapters):
        raise PartialSourceError("Incomplete chapter feed")
    summary = labels_from_feed(chapters)
    expected = range_labels(summary["labels"], lower, upper)
    if not expected:
        raise PartialSourceError("No English source chapters for approved batch")
    output.mkdir(parents=True, exist_ok=True)
    # The source may have nonconsecutive integer chapters and fractional labels.
    # Range boundaries are the lowest and highest actual English labels in this batch.
    result = runner(command(expected[0], expected[-1], output), check=False)
    report = inspect_and_stage(
        output, verified_output, expected, client_return_code=result.returncode,
        source_labels=summary["labels"],
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kainushi wa Akuma partial-source English CBZ batches")
    parser.add_argument("--batch", type=int, choices=tuple(RANGES), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verified-output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = run_batch(args.batch, args.output, args.verified_output)
        print(json.dumps({
            "title": TITLE, "batch": args.batch, "verified": report["verifiedCBZCount"],
            "expected": len(report["requestedLabels"]), "missing": report["missingLabelsWithinRequestedBatch"],
            "clientExitCode": report["clientExitCode"], "completeSourceBatch": report["completeAgainstMangaDexRequestedBatch"],
            "completeOriginalManga": False,
        }), flush=True)
        return 0 if report["completeAgainstMangaDexRequestedBatch"] else 1
    except (PartialSourceError, ReLIFEError, OSError, ValueError) as exc:
        print(f"Kainushi batch failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
