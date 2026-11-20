"""Bundle reviewed, source-identity-checked manga publication metadata candidates.

Only JSON metadata, NO page images, cover images, credentials, or HF access.
The ZIP contains one file per title, metadata-review.csv and manifest.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from manga_retriever.publication_metadata import (
    MAX_JSON_BYTES,
    SOURCE_TITLES,
    MetadataError,
    validate_local_candidate,
)


def make_bundle(source: Path, output: Path, *, require_all: bool = True) -> dict:
    if source.is_symlink() or not source.is_dir():
        raise MetadataError("Metadata source must be a real directory")
    if output.exists() or output.is_symlink() or output.resolve().is_relative_to(source.resolve()):
        raise MetadataError("Cannot overwrite or publish under metadata input")
    inputs = sorted(source.iterdir())
    if not inputs or any(p.is_symlink() or not p.is_file() or p.suffix != ".json"
                         or p.stat().st_size > MAX_JSON_BYTES for p in inputs):
        raise MetadataError("Metadata source must contain only safe JSON candidates")
    ids = {v["sourceId"]: k for k, v in SOURCE_TITLES.items()}
    seen: set[str] = set()
    files: dict[str, bytes] = {}
    rows: list[dict] = []
    for candidate_path in inputs:
        record = validate_local_candidate(candidate_path)
        slug = ids[record["match"]["sourceMangaId"]]
        if candidate_path.name != slug + ".json" or slug in seen:
            raise MetadataError("Metadata filename, identity or source is duplicated")
        seen.add(slug)
        meta = record["metadata"]
        missing = record.get("missing")
        if not isinstance(missing, list) or any(not isinstance(k, str) for k in missing):
            raise MetadataError("Malformed missing-fields list")
        data = json.dumps(record, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
        files[f"candidates/{slug}.json"] = data
        rows.append({
            "slug": slug,
            "title": meta["title"],
            "source": record["match"]["source"],
            "sourceMangaId": record["match"]["sourceMangaId"],
            "creatorCount": len(meta["creators"]),
            "tagCount": len(meta["tags"]),
            "hasEnglishSynopsis": bool(meta["synopsis"]),
            "hasCoverReference": bool(record["coverCandidate"]),
            "coverDownloaded": False,
            "publicationStatus": meta["publicationStatus"],
            "missing": "; ".join(missing),
            "requiresReview": True,
        })
    missing_slugs = sorted(set(SOURCE_TITLES) - seen)
    if require_all and missing_slugs:
        raise MetadataError("Incomplete manga metadata set: " + ", ".join(missing_slugs))
    rows.sort(key=lambda x: x["title"].casefold())
    columns = ["slug", "title", "source", "sourceMangaId", "creatorCount",
               "tagCount", "hasEnglishSynopsis", "hasCoverReference",
               "coverDownloaded", "publicationStatus", "missing", "requiresReview"]
    table = io.StringIO(newline="")
    writer = csv.DictWriter(table, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    files["metadata-review.csv"] = table.getvalue().encode("utf-8")
    report = {
        "schemaVersion": 1,
        "mediaKind": "manga",
        "bundleType": "publication-metadata-review",
        "records": len(seen),
        "complete": not missing_slugs,
        "missingSlugs": missing_slugs,
        "imageBytesDownloaded": 0,
        "coversDownloaded": 0,
        "privateCatalogueModified": False,
        "humanReviewRequired": True,
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "files": [
            {"path": name, "sha256": hashlib.sha256(data).hexdigest(),
             "bytes": len(data)}
            for name, data in sorted(files.items())
        ],
    }
    files["manifest.json"] = (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, tmp = tempfile.mkstemp(prefix=".metadata-review-", suffix=".zip", dir=output.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
                for name, data in sorted(files.items()):
                    archive.writestr(name, data)
        # Fail closed if the resulting archive is damaged.
        with zipfile.ZipFile(tmp) as archive:
            if archive.testzip() is not None:
                raise MetadataError("Resulting metadata bundle is corrupt")
        if output.exists():
            raise MetadataError("Output appeared during publication")
        Path(tmp).replace(output)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bundle 11 checked manga metadata candidates")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = make_bundle(args.source, args.output, require_all=not args.allow_partial)
    except (MetadataError, OSError, ValueError) as error:
        parser.exit(1, f"Metadata bundle failed: {error}\n")
    print(json.dumps({key: report[key] for key in
                      ("records", "complete", "missingSlugs", "coversDownloaded", "imageBytesDownloaded")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
