"""Offline, explicitly declared import of the creator's PDF manga volumes.

Give My Regards to Black Jack is offered for PDF download by Sato Manga Works.
No website is contacted: the owner must supply official PDF files and attest
that these are the distributor's own files, not scans of another edition.
Pages are rasterised to PNG, so PDF image bytes are *not* claimed as preserved.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from .importer import ImportFailure, import_local, natural_key, verify_export

SOURCE_URL = "https://densho810.com/free/"
TITLE = "Give My Regards to Black Jack"
AUTHOR = "SHUHO SATO"
MAX_FILES = 13
MAX_PAGES_PER_VOLUME = 500
MAX_PAGES_TOTAL = 4000
MAX_INPUT_PDF = 250_000_000
MAX_INPUT_TOTAL = 2_500_000_000
MAX_OUTPUT_PAGE = 25_000_000
MAX_OUTPUT_TOTAL = 5_000_000_000
MAX_PIXELS = 70_000_000


def _digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _files(source: Path, expected_volumes: int | None) -> list[Path]:
    if not source.is_dir() or source.is_symlink():
        raise ImportFailure("Source must be a real local PDF directory")
    files = sorted(source.iterdir(), key=lambda p: natural_key(p.name))
    if not 1 <= len(files) <= MAX_FILES or (expected_volumes is not None and len(files) != expected_volumes):
        raise ImportFailure("Expected 1 to 13 PDFs, matching the declared volume count")
    total = 0
    for path in files:
        if (path.is_symlink() or not path.is_file() or path.suffix.lower() != ".pdf"
                or any(ch in path.name for ch in ("/", "\\", "\x00"))):
            raise ImportFailure("PDF directory may contain only regular PDF files")
        size = path.stat().st_size
        if not 1 <= size <= MAX_INPUT_PDF:
            raise ImportFailure("PDF size outside allowed bounds")
        total += size
        if total > MAX_INPUT_TOTAL:
            raise ImportFailure("PDF source directory exceeds input quota")
        with path.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                raise ImportFailure("PDF file signature mismatch")
    return files


def import_blackjack_pdfs(
    source: Path, output: Path, registry: Path, *, official_source_declared: bool,
    expected_volumes: int | None = None, scale: float = 2.0,
) -> dict[str, int]:
    """Render owner-provided official PDFs and verify locally before publishing.

    The declaration is an owner assertion, not cryptographic proof of rights.
    Changes are not made to originals and no cloud upload takes place.
    """
    if not official_source_declared:
        raise ImportFailure("Confirm --official-source only for PDFs downloaded from Sato Manga Works")
    if type(expected_volumes) is not int and expected_volumes is not None:
        raise ImportFailure("Invalid expected volume count")
    if expected_volumes is not None and not 1 <= expected_volumes <= MAX_FILES:
        raise ImportFailure("Invalid expected volume count")
    if not isinstance(scale, (int, float)) or not math.isfinite(scale) or scale not in (1.5, 2.0, 2.5):
        raise ImportFailure("Use a bounded raster scale of 1.5, 2 or 2.5")
    source, output, registry = Path(source), Path(output), Path(registry)
    if output.exists() or output.is_symlink():
        raise ImportFailure("Destination already exists; no automatic overwrite")
    if output.resolve().is_relative_to(source.resolve()) or registry.resolve().is_relative_to(source.resolve()):
        raise ImportFailure("Export and registry must be outside source PDF folder")
    files = _files(source, expected_volumes)
    try:
        import pypdfium2 as pdfium
    except ImportError as error:
        raise ImportFailure('Install PDF support: python -m pip install -e ".[pdf]"') from error
    output.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=".blackjack-pdf-stage-", dir=output.parent))
    try:
        images_root = work / "input" / TITLE
        total_pages = 0
        total_bytes = 0
        volume_info = []
        for order, path in enumerate(files, 1):
            folder = images_root / f"Volume {order:02d}"
            folder.mkdir(parents=True)
            try:
                document = pdfium.PdfDocument(str(path))
            except Exception as error:
                raise ImportFailure(f"Unreadable or protected PDF volume {order}") from error
            try:
                count = len(document)
                if not 1 <= count <= MAX_PAGES_PER_VOLUME or total_pages + count > MAX_PAGES_TOTAL:
                    raise ImportFailure("PDF page count exceeds configured limits")
                for index in range(count):
                    page = document.get_page(index)
                    try:
                        width, height = page.get_size()
                        pixels = math.ceil(width * scale) * math.ceil(height * scale)
                        if (not math.isfinite(pixels) or pixels < 1 or pixels > MAX_PIXELS
                                or width <= 0 or height <= 0):
                            raise ImportFailure("PDF page dimensions outside rendering limits")
                        bitmap = page.render(scale=scale)
                        try:
                            image = bitmap.to_pil()
                            target = folder / f"{index + 1:04d}.png"
                            image.save(target, format="PNG")
                            image.close()
                        finally:
                            bitmap.close()
                        size = target.stat().st_size
                        if not 1 <= size <= MAX_OUTPUT_PAGE:
                            raise ImportFailure("Rendered page exceeds page quota")
                        total_bytes += size
                        if total_bytes > MAX_OUTPUT_TOTAL:
                            raise ImportFailure("Rendered pages exceed import quota")
                    finally:
                        page.close()
                total_pages += count
            finally:
                document.close()
            volume_info.append({"volume": order, "originalFile": path.name,
                                "sha256": _digest(path), "pages": count})
        rights = {
            "schemaVersion": 1,
            "sourceType": "licensed",
            "title": TITLE,
            "permissionEvidence": SOURCE_URL + " (creator's official PDF download terms)",
            "attribution": (
                "Give My Regards to Black Jack / ブラックジャックによろしく; "
                "SHUHO SATO / 佐藤秀峰. Original publisher PDFs only. "
                "Review Sato Manga Works terms: attribution, ebook-store, music and reporting duties."
            ),
            "recordedAt": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        rights_path = work / "rights.json"
        rights_path.write_text(json.dumps(rights, indent=2) + "\n", encoding="utf-8")
        staged = work / "verified"
        result = import_local(work / "input", staged, registry, rights_path=rights_path, direction="rtl")
        manifest_path = staged / "download_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["sourcePdfProvenance"] = {
            "source": SOURCE_URL, "title": TITLE, "author": AUTHOR,
            "originDeclaredByOwner": True, "publisherFileAuthenticityIndependentlyVerified": False,
            "rasterFormat": "PNG", "renderScale": scale, "originalPdfBytesPreserved": False,
            "volumes": volume_info,
            "reuseTerms": "Creator-specific terms apply; post-publication reporting may be required",
        }
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if verify_export(staged) != result or result["chapters"] != len(files) or result["pages"] != total_pages:
            raise ImportFailure("Rasterised manga export failed final verification")
        if output.exists() or output.is_symlink():
            raise ImportFailure("Destination appeared during import")
        staged.rename(output)
        return result
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Import creator-supplied PDF manga volumes to verified CBZ")
    parser.add_argument("--source", required=True, type=Path, help="Local folder with official PDFs only")
    parser.add_argument("--output", required=True, type=Path, help="New output directory")
    parser.add_argument("--registry", type=Path, default=Path(".manga-retriever/ids.json"))
    parser.add_argument("--expected-volumes", type=int)
    parser.add_argument("--scale", type=float, choices=[1.5, 2.0, 2.5], default=2.0)
    parser.add_argument("--official-source", action="store_true", help="Declare original files came from Sato Manga Works")
    args = parser.parse_args(argv)
    try:
        counts = import_blackjack_pdfs(args.source, args.output, args.registry,
                                       expected_volumes=args.expected_volumes, scale=args.scale,
                                       official_source_declared=args.official_source)
    except (ImportFailure, OSError, ValueError) as error:
        print(f"PDF manga import failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "verified", **counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
