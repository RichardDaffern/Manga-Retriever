"""Five allowlisted Love So Life English bonus chapters, independent CBZ verification."""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from manga_retriever.relife import ReLIFEError, _inspect_cbz, _safe_output
from scripts.source_probe_eight import MangaDexMetadata

TITLE_ID = "911a12ae-1022-448e-9219-b7b294d7fb3e"
BONUS_LABELS = ("33.5", "33.6", "63.5", "75.5", "99.5")
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
FILENAME = re.compile(r"\bch(?:apter)?\.?\s*(\d+(?:\.\d+)?)(?=\b|$)", re.IGNORECASE)


class BonusError(ValueError):
    """Unsafe or incompletely verified bonus-chapter download."""


def find_bonus_chapters(entries: list[dict]) -> dict[str, str]:
    selected = {}
    for label in BONUS_LABELS:
        matches = [
            c for c in entries
            if isinstance(c, dict)
            and isinstance(c.get("attributes"), dict)
            and c["attributes"].get("chapter") == label
            and not c["attributes"].get("externalUrl")
            and isinstance(c.get("id"), str) and UUID.fullmatch(c["id"])
        ]
        if matches:
            selected[label] = matches[0]["id"]
    return selected


def command(chapter_id: str, folder: Path) -> list[str]:
    _safe_output(folder)
    if not UUID.fullmatch(chapter_id):
        raise BonusError("Invalid chapter source ID")
    return [
        sys.executable, "-m", "mangadex_downloader",
        "https://mangadex.org/chapter/" + chapter_id,
        "--language", "en", "--save-as", "cbz", "--path", str(folder),
        "--http-retries", "3", "--delay-requests", "2",
    ]


def run_bonuses(output: Path, verified: Path, *, client=None, runner=subprocess.run,
                module_exists=importlib.util.find_spec) -> dict:
    if module_exists("mangadex_downloader") is None:
        raise BonusError("Pinned mangadex-downloader==3.1.4 is required")
    _safe_output(output)
    _safe_output(verified)
    if verified.exists():
        raise BonusError("Refusing to overwrite verified manga")
    output.mkdir(parents=True, exist_ok=True)
    verified.mkdir(parents=True)
    client = client or MangaDexMetadata(delay=2)
    total, chapters = client.feed(TITLE_ID)
    if len(chapters) != total:
        raise BonusError("Incomplete chapter feed")
    available = find_bonus_chapters(chapters)
    records = []
    failures = {}
    for label in BONUS_LABELS:
        chapter_id = available.get(label)
        if chapter_id is None:
            failures[label] = "Not present as an English hosted chapter"
            continue
        folder = output / label
        folder.mkdir()
        completed = runner(command(chapter_id, folder), check=False)
        if completed.returncode:
            failures[label] = f"Downloader exited {completed.returncode}"
            continue
        found = list(folder.rglob("*.cbz"))
        if len(found) != 1 or any(p.is_symlink() for p in folder.rglob("*")):
            failures[label] = f"Expected exactly one CBZ for label {label}; found {len(found)}"
            continue
        name_match = FILENAME.search(found[0].stem)
        if name_match is None or name_match.group(1) != label:
            failures[label] = "Cannot independently match CBZ filename with source chapter label"
            continue
        try:
            details = _inspect_cbz(found[0])
        except (ReLIFEError, OSError, ValueError):
            failures[label] = "Image page integrity verification failed"
            continue
        destination = verified / "chapters" / f"bonus-{label}" / found[0].name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(found[0], destination)
        if _inspect_cbz(destination)["sha256"] != details["sha256"]:
            raise BonusError("Staged copy integrity mismatch")
        records.append({
            "label": label, "chapterId": chapter_id, "relativePath": destination.relative_to(verified).as_posix(),
            "sha256": details["sha256"], "pages": details["verifiedPageCount"],
        })
    completed_labels = {r["label"] for r in records}
    missing = [label for label in BONUS_LABELS if label not in completed_labels]
    report = {
        "schemaVersion": 1,
        "title": "Love So Life",
        "source": "MangaDex uploaded-original English scanlation chapters",
        "sourceMangaId": TITLE_ID,
        "expectedUniqueDecimalExtras": list(BONUS_LABELS),
        "verifiedDecimalExtras": sorted(completed_labels),
        "missingDecimalExtras": missing,
        "failures": failures,
        "allFiveExtrasVerified": not missing,
        "completeManga": False,
        "rights": "No publisher-master or unrestricted public redistribution rights asserted",
        "createdAtUtc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archives": records,
    }
    (verified / "bonus_quality_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (verified / "SOURCE_AND_RIGHTS.txt").write_text(
        "Love So Life by Kaede Kouchi. Source: MangaDex English scanlation uploads.\n"
        "https://mangadex.org/title/" + TITLE_ID + "\n"
        "Attribute MangaDex, original creator and the relevant scanlation groups.\n"
        "This is an extra-chapter-only archive; see individual results and use restrictions in JSON.\n",
        encoding="utf-8",
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download exactly five Love So Life English extras")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verified-output", type=Path, required=True)
    options = parser.parse_args(argv)
    try:
        result = run_bonuses(options.output, options.verified_output)
        print(json.dumps({"verifiedExtras": result["verifiedDecimalExtras"],
                          "missingExtras": result["missingDecimalExtras"],
                          "allExtrasVerified": result["allFiveExtrasVerified"]}), flush=True)
        return 0 if result["allFiveExtrasVerified"] else 1
    except (BonusError, OSError, ReLIFEError, ValueError) as exc:
        print(f"Love So Life extras error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
