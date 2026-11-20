"""Produce English-only original-image ZIP and EPUB from an authorised, verified export.

This first GitHub Actions source is fixed to creator-licensed Pepper&Carrot
episode 26. Do not reuse its source-specific rights check for other titles.
No remote fetch is performed here. Original image bytes are never transcoded.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from .importer import ImportFailure, _validate_image, verify_export

TITLE = "Pepper&Carrot - Episode 26: Books Are Great"
SOURCE_URL = "https://www.peppercarrot.com/en/webcomic-sources/ep26_Books-Are-Great.html"
LICENCE_URL = "https://creativecommons.org/licenses/by/4.0/"
ATTRIBUTION = (
    "Pepper&Carrot, Episode 26: Books Are Great\n"
    "Art and scenario: David Revoy\n"
    "English translation and lettering: see original episode credits\n"
    f"Full credits and original source: {SOURCE_URL}\n"
    f"Licence: Creative Commons Attribution 4.0, {LICENCE_URL}\n"
    "Unmodified source JPEG image bytes.\n"
)
EPUB_MIME = b"application/epub+zip"
EXPECTED_PAGES = 6
IMAGE_LIMIT = 25_000_000


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def verified_english_pages(export: Path) -> list[tuple[str, bytes, str]]:
    """Return (filename, original bytes, sha256) only for the fixed licensed source."""
    if export.is_symlink() or not export.is_dir():
        raise ImportFailure("Verified export is missing")
    checked = verify_export(export)
    if checked != {"series": 1, "chapters": 1, "pages": EXPECTED_PAGES}:
        raise ImportFailure("Incorrect verified source page count")
    source = json.loads((export / "download_manifest.json").read_text(encoding="utf-8"))
    rights = json.loads((export / "controller_candidate" / "rights.json").read_text(encoding="utf-8"))
    proof = source.get("licensedSource") or {}
    if (proof.get("provider") != "peppercarrot" or proof.get("episode") != 26
            or proof.get("language") != "en" or proof.get("licence") != "CC BY 4.0"
            or proof.get("licenceUrl") != LICENCE_URL or proof.get("sourcePage") != SOURCE_URL
            or rights.get("sourceType") != "licensed" or SOURCE_URL not in rights.get("attribution", "")):
        raise ImportFailure("Explicitly authorised English source provenance is missing")
    records = proof.get("pages")
    if not isinstance(records, list) or len(records) != EXPECTED_PAGES:
        raise ImportFailure("Original page attribution records are incomplete")
    root = (export / "controller_candidate" / "assets").resolve()
    images: list[tuple[str, bytes, str]] = []
    for expected, record in enumerate(records, start=1):
        if not isinstance(record, dict) or record.get("pageNumber") != expected:
            raise ImportFailure("Source page sequence mismatch")
        path = record.get("assetPath")
        claimed_hash = record.get("sha256")
        if (not isinstance(path, str) or not path.startswith("manga/")
                or not path.endswith(".jpg") or not isinstance(claimed_hash, str)
                or len(claimed_hash) != 64):
            raise ImportFailure("Unexpected page location, type or hash")
        file = root / path
        if file.is_symlink() or not file.resolve().is_relative_to(root) or not file.is_file():
            raise ImportFailure("Source page path is unsafe or unavailable")
        if not 0 < file.stat().st_size <= IMAGE_LIMIT:
            raise ImportFailure("Page exceeds image limit")
        data = file.read_bytes()
        filename = f"{expected:04d}.jpg"
        metrics = _validate_image(data, filename)
        if digest(data) != claimed_hash or metrics["sha256"] != claimed_hash:
            raise ImportFailure("Source image hash mismatch")
        images.append((filename, data, claimed_hash))
    return images


def _archive_image_zip(output: Path, pages: list[tuple[str, bytes, str]]) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        for filename, data, _ in pages:
            archive.writestr("pages/" + filename, data)
        archive.writestr("ATTRIBUTION.txt", ATTRIBUTION.encode())
        manifest = {
            "schemaVersion": 1, "language": "en", "title": TITLE,
            "mediaKind": "manga", "sourceUrl": SOURCE_URL, "licence": LICENCE_URL,
            "pages": [{"name": "pages/" + name, "sha256": sha} for name, _, sha in pages],
        }
        archive.writestr("manifest.json", json.dumps(manifest, indent=2).encode())


def _epub_page(number: int) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">'
        '<head><title>Page ' + str(number) + '</title>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>'
        '<style>html,body{margin:0;padding:0;background:white;}'
        'img{display:block;width:100%;height:auto;}</style></head>'
        '<body><img alt="Page ' + str(number) + '" src="../images/p' +
        f"{number:04d}.jpg" + '"/></body></html>'
    )


def _archive_epub(output: Path, pages: list[tuple[str, bytes, str]]) -> None:
    items: list[str] = []
    spine: list[str] = []
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=False) as archive:
        # EPUB requires an uncompressed mimetype as the first member.
        archive.writestr("mimetype", EPUB_MIME, compress_type=zipfile.ZIP_STORED)
        archive.writestr("META-INF/container.xml",
                         '<?xml version="1.0" encoding="UTF-8"?>'
                         '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                         '<rootfiles><rootfile full-path="EPUB/package.opf" '
                         'media-type="application/oebps-package+xml"/>'
                         '</rootfiles></container>')
        archive.writestr("EPUB/nav.xhtml",
                         '<?xml version="1.0" encoding="utf-8"?>'
                         '<html xmlns="http://www.w3.org/1999/xhtml" '
                         'xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en">'
                         '<head><title>Contents</title></head><body>'
                         '<nav epub:type="toc"><h1>Contents</h1><ol>'
                         '<li><a href="pages/p0001.xhtml">Episode 26</a></li>'
                         '</ol></nav></body></html>')
        for index, (_, data, _) in enumerate(pages, start=1):
            ident = f"p{index:04d}"
            archive.writestr(f"EPUB/images/{ident}.jpg", data)
            archive.writestr(f"EPUB/pages/{ident}.xhtml", _epub_page(index))
            items.append(f'<item id="i{ident}" href="images/{ident}.jpg" media-type="image/jpeg"/>')
            items.append(f'<item id="{ident}" href="pages/{ident}.xhtml" '
                         'media-type="application/xhtml+xml"/>')
            spine.append(f'<itemref idref="{ident}"/>')
        package = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
            'unique-identifier="bookid" xml:lang="en">'
            '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
            '<dc:identifier id="bookid">urn:taiyou:licensed:peppercarrot:en:26</dc:identifier>'
            f'<dc:title>{escape(TITLE)}</dc:title>'
            '<dc:creator>David Revoy</dc:creator><dc:language>en</dc:language>'
            f'<dc:rights>CC BY 4.0: {LICENCE_URL}</dc:rights>'
            f'<dc:source>{SOURCE_URL}</dc:source>'
            f'<dc:description>{escape(ATTRIBUTION)}</dc:description>'
            '<meta property="rendition:layout">pre-paginated</meta></metadata>'
            '<manifest><item id="nav" href="nav.xhtml" '
            'media-type="application/xhtml+xml" properties="nav"/>'
            + "".join(items) + '</manifest>'
            '<spine page-progression-direction="ltr">' + "".join(spine) + '</spine></package>'
        )
        archive.writestr("EPUB/package.opf", package)
        archive.writestr("EPUB/ATTRIBUTION.txt", ATTRIBUTION)


def _verify_outputs(folder: Path, pages: list[tuple[str, bytes, str]]) -> None:
    expected = {name: sha for name, _, sha in pages}
    image_zip = folder / "english-original-images.zip"
    epub = folder / "english-fixed-layout.epub"
    for filename, prefix in ((image_zip, "pages/"), (epub, "EPUB/images/p")):
        with zipfile.ZipFile(filename) as book:
            if book.testzip() is not None:
                raise ImportFailure("Corrupted output archive")
            for name, sha in expected.items():
                member = prefix + name
                if digest(book.read(member)) != sha:
                    raise ImportFailure("Output image differs from source image")
    with zipfile.ZipFile(epub) as book:
        if book.namelist()[0] != "mimetype" or book.read("mimetype") != EPUB_MIME:
            raise ImportFailure("Invalid EPUB mimetype or member order")
        if book.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            raise ImportFailure("EPUB mimetype must be uncompressed")
        for number in range(1, EXPECTED_PAGES + 1):
            if not book.read(f"EPUB/pages/p{number:04d}.xhtml"):
                raise ImportFailure("Missing EPUB reader page")


def package_verified_export(export: Path, output: Path) -> dict:
    if output.exists() or output.is_symlink():
        raise ImportFailure("Output already exists")
    pages = verified_english_pages(export)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".alternative-formats-", dir=output.parent))
    try:
        _archive_image_zip(stage / "english-original-images.zip", pages)
        _archive_epub(stage / "english-fixed-layout.epub", pages)
        _verify_outputs(stage, pages)
        result = {
            "status": "verified-media", "language": "en", "title": TITLE,
            "source": SOURCE_URL, "licence": "CC BY 4.0", "pages": len(pages),
            "formats": [
                {"name": filename, "sha256": digest((stage / filename).read_bytes()),
                 "size": (stage / filename).stat().st_size}
                for filename in ("english-original-images.zip", "english-fixed-layout.epub")
            ],
        }
        (stage / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        (stage / "ATTRIBUTION.txt").write_text(ATTRIBUTION, encoding="utf-8")
        stage.rename(output)
        return result
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Package verified licensed English pages as ZIP and EPUB")
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = package_verified_export(args.export, args.output)
    except (ImportFailure, OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f"Alternative format packaging failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
