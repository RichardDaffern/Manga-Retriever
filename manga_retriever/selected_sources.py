"""Allowlisted fixed-title MangaDex acquisition and independent CBZ verification.

Uses the externally installed MangaDex downloader. No arbitrary URL inputs,
credential bypass or DRM removal. Intended for files the user can lawfully keep.
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
from pathlib import Path

from .relife import MAX_ARCHIVES, MAX_AUDIT_BYTES, ReLIFEError, _inspect_cbz, _safe_output

SOURCES = {
    "love-so-life": {
        "title": "Love So Life", "id": "911a12ae-1022-448e-9219-b7b294d7fb3e", "chapters": 106,
    },
    "maid-sama": {
        "title": "Kaichou wa Maid-sama!", "id": "d5e2bd89-e300-4262-a799-fb4f79bdb777", "chapters": 85,
    },
    "last-game": {
        "title": "Last Game", "id": "32600d3f-a43a-4f90-8a4e-c4e09f35c99b", "chapters": 56,
    },
    "onizuka-sawarida": {
        "title": "Onizuka-chan and Sawarida-kun", "id": "96b87943-6458-4045-a029-d3185d5cea57", "chapters": 49,
    },
}
CHAPTER_LABEL = re.compile(r"\bch(?:apter)?\.?\s*(\d+)(\.\d+)?(?=\b|$)", re.IGNORECASE)


class SelectedSourceError(ValueError):
    """Invalid request, incomplete download, or unverifiable chapter data."""


def chapter_range(slug: str, start: int, end: int) -> None:
    if slug not in SOURCES or type(start) is not int or type(end) is not int:
        raise SelectedSourceError("Unapproved manga source or chapter bounds")
    if not 1 <= start <= end <= SOURCES[slug]["chapters"] or end - start + 1 > 20:
        raise SelectedSourceError("Chapter range must contain 1–20 approved numbered chapters")


def command(slug: str, start: int, end: int, output: Path) -> list[str]:
    """Exact title URL, English-only uploader-original images, never data-saver."""
    chapter_range(slug, start, end)
    _safe_output(output)
    return [
        sys.executable, "-m", "mangadex_downloader",
        f"https://mangadex.org/title/{SOURCES[slug]['id']}",
        "--language", "en", "--save-as", "cbz", "--path", str(output),
        "--start-chapter", str(start), "--end-chapter", str(end),
        "--order", "oldest", "--http-retries", "3", "--delay-requests", "2",
    ]


def download(slug: str, start: int, end: int, output: Path, *, acknowledge_rights: bool,
             run=subprocess.run, module_exists=importlib.util.find_spec) -> None:
    if not acknowledge_rights:
        raise SelectedSourceError("Confirm that obtaining and keeping these scans is authorised")
    argv = command(slug, start, end, output)
    if module_exists("mangadex_downloader") is None:
        raise SelectedSourceError("Install mangadex-downloader==3.1.4 first")
    output.mkdir(parents=True, exist_ok=True)
    result = run(argv, check=False)
    if result.returncode:
        raise SelectedSourceError("MangaDex client failed; download incomplete")


def number_from_cbz(filename: str) -> int | None:
    """Count integer main chapters only; never allow 1.5 to stand in for 1."""
    match = CHAPTER_LABEL.search(Path(filename).stem)
    if match is None or match.group(2) is not None:
        return None
    return int(match.group(1))


def audit(slug: str, start: int, end: int, folder: Path) -> dict:
    chapter_range(slug, start, end)
    if folder.is_symlink() or not folder.is_dir() or any(p.is_symlink() for p in folder.rglob("*")):
        raise SelectedSourceError("Missing or symlinked manga output")
    cbzs = sorted(folder.rglob("*.cbz"))
    if not 1 <= len(cbzs) <= MAX_ARCHIVES:
        raise SelectedSourceError("Missing or excessive CBZ files")
    if sum(p.stat().st_size for p in cbzs) > MAX_AUDIT_BYTES:
        raise SelectedSourceError("Manga output exceeds audit budget")
    expected = set(range(start, end + 1))
    found: set[int] = set()
    verified = []
    extras = []
    for file in cbzs:
        rel = file.relative_to(folder).as_posix()
        try:
            record = _inspect_cbz(file)
        except ReLIFEError as error:
            raise SelectedSourceError(f"Corrupt chapter archive: {rel}") from error
        number = number_from_cbz(file.name)
        if number is None:
            extras.append(rel)
        elif number in found or number not in expected:
            raise SelectedSourceError(f"Duplicate or unexpected main chapter label: {rel}")
        else:
            found.add(number)
        record["relativePath"] = rel
        record["mainChapterLabel"] = number
        verified.append(record)
    missing = sorted(expected - found)
    if missing:
        raise SelectedSourceError(f"Missing numbered chapters: {missing}")
    return {
        "schemaVersion": 1,
        "source": "MangaDex English uploaded-original image endpoints; not publisher masters",
        "sourceTitleUrl": f"https://mangadex.org/title/{SOURCES[slug]['id']}",
        "title": SOURCES[slug]["title"], "slug": slug,
        "requestedRange": {"start": start, "end": end},
        "verifiedMainChapterNumbers": sorted(found),
        "verifiedMainChapters": len(found),
        "verifiedArchives": len(verified),
        "verifiedPages": sum(x["verifiedPageCount"] for x in verified),
        "extraChapterArchivePaths": extras,
        "completeSeriesVerified": False,
        "qualityRequested": "original-upload-not-data-saver",
        "caveat": "File-name chapter identity and page hashes verified, not publisher-master fidelity or legal download permissions",
        "auditedAtUtc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "archives": verified,
    }


def publish_verified(folder: Path, report: dict, target: Path) -> None:
    """Stage only checked CBZs, their SHA report and a source credit notice."""
    _safe_output(target)
    if target.exists():
        raise SelectedSourceError("Refuse to overwrite existing verified export")
    target.mkdir(parents=True)
    try:
        for item in report["archives"]:
            source = folder / item["relativePath"]
            dest = target / "chapters" / item["relativePath"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            if _inspect_cbz(dest)["sha256"] != item["sha256"]:
                raise SelectedSourceError("Exported CBZ checksum changed")
        (target / "quality_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (target / "SOURCE_AND_RIGHTS.txt").write_text(
            f"{report['title']}. MangaDex English scanlation uploads.\n"
            f"Listing: {report['sourceTitleUrl']}\n"
            "Credit original creator and the contributing scanlation group.\n"
            "No publisher-master quality, ownership or redistribution rights are asserted.\n",
            encoding="utf-8",
        )
    except Exception:
        shutil.rmtree(target)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fixed MangaDex manga sources, original quality, verified local CBZs")
    parser.add_argument("--slug", choices=tuple(SOURCES), required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verified-output", type=Path, required=True)
    parser.add_argument("--acknowledge-rights", action="store_true")
    args = parser.parse_args(argv)
    try:
        download(args.slug, args.start, args.end, args.output, acknowledge_rights=args.acknowledge_rights)
        report = audit(args.slug, args.start, args.end, args.output)
        publish_verified(args.output, report, args.verified_output)
        print(json.dumps({"status": "verified", "slug": args.slug, "chapters": report["verifiedMainChapters"],
                          "pages": report["verifiedPages"], "verifiedOutput": str(args.verified_output)}))
        return 0
    except (SelectedSourceError, ReLIFEError, OSError, ValueError) as exc:
        print(f"Manga download verification failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
