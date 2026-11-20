"""Safely import owner-supplied DRM-free English image EPUBs.

Reads EPUB spine page order; accepts fixed-layout XHTML with one embedded image
per page. Converts only the container: source JPEG/PNG/WebP/AVIF bytes remain
unchanged. The resulting bundle is built by the existing verified v1 importer.
No remote access, login automation, DRM removal or rights claims are performed.
"""
from __future__ import annotations

import argparse
import json
import posixpath
import re
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

from .importer import ImportFailure, MAX_IMAGE, MIME, _validate_image, import_local, verify_export

MAX_EPUB_BYTES = 1_000_000_000
MAX_UNCOMPRESSED = 2_000_000_000
MAX_ENTRIES = 12_000
MAX_SPINE_PAGES = 1_000
MAX_DOCUMENT = 2_000_000
ALLOWED_LANGUAGES = {"en", "en-us", "en-gb", "en-au", "en-ca", "eng"}


def _xml(data: bytes) -> ET.Element:
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ImportFailure("EPUB XML must not contain a DTD or entities")
    try:
        return ET.fromstring(data)  # noqa: S314 - DTD and entity declarations rejected above
    except ET.ParseError as exc:
        raise ImportFailure("Malformed EPUB metadata or page XML") from exc


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _safe_path(raw: str) -> str:
    if not isinstance(raw, str) or not raw or len(raw) > 300 or "\x00" in raw or "\\" in raw:
        raise ImportFailure("Unsafe EPUB member name")
    decoded = unquote(raw)
    if "%" in decoded or not decoded or decoded.startswith("/") or ":" in decoded:
        raise ImportFailure("Unsafe EPUB member URL")
    parts = PurePosixPath(decoded).parts
    if ".." in parts or not parts or len(parts) > 20:
        raise ImportFailure("Unsafe EPUB member traversal")
    result = posixpath.normpath(decoded)
    if result.startswith("../") or result in {"", ".", ".."}:
        raise ImportFailure("Unsafe EPUB member path")
    return result


def _resolve(base: str, raw: str) -> str:
    url = urlsplit(raw)
    if url.scheme or url.netloc or url.query or url.fragment:
        raise ImportFailure("External or ambiguous EPUB image URL")
    # Relative ../ links are normal in EPUB; constrain their final destination.
    if not url.path or url.path.startswith("/") or "\\" in url.path:
        raise ImportFailure("Invalid EPUB relative reference")
    decoded = unquote(url.path)
    if "%" in decoded or ":" in decoded or decoded.startswith("/"):
        raise ImportFailure("Invalid EPUB URL encoding")
    combined = posixpath.normpath(posixpath.join(posixpath.dirname(base), decoded))
    return _safe_path(combined)


def _entries(book: zipfile.ZipFile) -> set[str]:
    entries: set[str] = set()
    total = 0
    members = book.infolist()
    if not 1 <= len(members) <= MAX_ENTRIES:
        raise ImportFailure("EPUB entry limit exceeded")
    for member in members:
        name = member.filename
        if member.is_dir():
            _safe_path(name.rstrip("/"))
            continue
        normalised = _safe_path(name)
        if normalised != name or normalised.casefold() in entries or member.flag_bits & 1:
            raise ImportFailure("Duplicate, encrypted or noncanonical EPUB entry")
        mode = member.external_attr >> 16
        if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
            raise ImportFailure("EPUB contains symbolic links or special members")
        if member.file_size > MAX_EPUB_BYTES or member.file_size < 0:
            raise ImportFailure("Oversized EPUB member")
        if member.file_size > max(member.compress_size, 1) * 100:
            raise ImportFailure("Suspicious EPUB compression ratio")
        total += member.file_size
        if total > MAX_UNCOMPRESSED:
            raise ImportFailure("EPUB exceeds decompressed size quota")
        entries.add(normalised.casefold())
    if "meta-inf/encryption.xml" in entries:
        raise ImportFailure("DRM/encrypted EPUB unsupported")
    return entries


def _read(book: zipfile.ZipFile, name: str, maximum: int) -> bytes:
    name = _safe_path(name)
    try:
        info = book.getinfo(name)
        if not 0 < info.file_size <= maximum:
            raise ImportFailure("Oversized or empty EPUB resource")
        with book.open(info) as file:
            result = file.read(maximum + 1)
    except (KeyError, OSError, RuntimeError, EOFError, zipfile.BadZipFile) as exc:
        raise ImportFailure("Missing or corrupt EPUB resource") from exc
    if len(result) != info.file_size or len(result) > maximum:
        raise ImportFailure("EPUB resource size mismatch")
    return result


def extract_images(epub: Path, dest: Path) -> dict:
    """Extract image pages in spine order into one chapter folder, without transcoding."""
    if epub.is_symlink() or not epub.is_file() or epub.suffix.lower() != ".epub":
        raise ImportFailure("Only regular local EPUB files accepted")
    if not 0 < epub.stat().st_size <= MAX_EPUB_BYTES:
        raise ImportFailure("EPUB file exceeds quota")
    try:
        with zipfile.ZipFile(epub) as book:
            _entries(book)
            if _read(book, "mimetype", 60) != b"application/epub+zip":
                raise ImportFailure("Invalid EPUB mimetype")
            container = _xml(_read(book, "META-INF/container.xml", MAX_DOCUMENT))
            roots = [item.attrib.get("full-path") for item in container.iter()
                     if _local(item.tag) == "rootfile"]
            if len(roots) != 1 or not roots[0]:
                raise ImportFailure("EPUB must have exactly one package")
            opf_path = _safe_path(roots[0])
            package = _xml(_read(book, opf_path, MAX_DOCUMENT))
            languages = [(item.text or "").strip().casefold() for item in package.iter()
                         if _local(item.tag) == "language"]
            if not languages or any(value not in ALLOWED_LANGUAGES for value in languages):
                raise ImportFailure("Only explicitly English EPUB publications accepted")
            titles = [(item.text or "").strip() for item in package.iter()
                      if _local(item.tag) == "title" and (item.text or "").strip()]
            if not titles:
                raise ImportFailure("Missing EPUB publication title")
            manifest = next((item for item in package.iter() if _local(item.tag) == "manifest"), None)
            spine = next((item for item in package.iter() if _local(item.tag) == "spine"), None)
            if manifest is None or spine is None:
                raise ImportFailure("Missing EPUB manifest or reading order")
            items = {}
            for item in manifest:
                if _local(item.tag) != "item":
                    continue
                ident, href, media = item.attrib.get("id"), item.attrib.get("href"), item.attrib.get("media-type")
                if not ident or not href or not media or ident in items:
                    raise ImportFailure("Malformed EPUB manifest")
                items[ident] = (_resolve(opf_path, href), media)
            refs = [item.attrib.get("idref") for item in spine if _local(item.tag) == "itemref"]
            if not 1 <= len(refs) <= MAX_SPINE_PAGES or any(not ref or ref not in items for ref in refs):
                raise ImportFailure("Unsupported or empty EPUB page spine")
            dest.mkdir(parents=True, exist_ok=False)
            hashes: set[str] = set()
            for number, ref in enumerate(refs, 1):
                page_path, page_type = items[ref]
                if page_type != "application/xhtml+xml":
                    raise ImportFailure("Only fixed-layout image XHTML spine items supported")
                page = _xml(_read(book, page_path, MAX_DOCUMENT))
                body = next((e for e in page.iter() if _local(e.tag) == "body"), None)
                if body is None:
                    raise ImportFailure("EPUB page body missing")
                links = []
                for element in body.iter():
                    if _local(element.tag) == "img":
                        links.append(element.attrib.get("src"))
                    elif _local(element.tag) == "image":
                        links.append(next((v for k, v in element.attrib.items()
                                           if _local(k) == "href"), None))
                if len(links) != 1 or not links[0]:
                    raise ImportFailure("Expected one image on each fixed-layout page")
                image_path = _resolve(page_path, links[0])
                suffix = Path(image_path).suffix.lower()
                if suffix not in MIME:
                    raise ImportFailure("Unsupported EPUB image format")
                data = _read(book, image_path, MAX_IMAGE)
                verified = _validate_image(data, f"{number:04d}{suffix}")
                if verified["sha256"] in hashes:
                    raise ImportFailure("Duplicate EPUB page image")
                hashes.add(verified["sha256"])
                (dest / f"{number:04d}{suffix}").write_bytes(data)
            return {"title": titles[0], "language": "en", "pages": len(refs)}
    except (zipfile.BadZipFile, OSError, RuntimeError, EOFError) as exc:
        raise ImportFailure("Invalid or damaged EPUB archive") from exc


def _folder_name(value: str) -> str:
    safe = "".join(ch for ch in value if ch.isalnum() or ch in " -_.()")
    safe = safe.strip(" .")[:120]
    if not safe or safe in {".", ".."}:
        raise ImportFailure("Invalid EPUB series or volume title")
    return safe


def import_epubs(source: Path, output: Path, registry: Path, *, series_title: str | None = None,
                 acknowledge_rights: bool = False) -> dict:
    """Import local English, DRM-free EPUBs as volume-labelled image chapters."""
    if not acknowledge_rights:
        raise ImportFailure("Confirm you are authorised to import and retain these EPUB files")
    if source.is_symlink() or not source.exists() or output.exists() or output.is_symlink():
        raise ImportFailure("Input unavailable or destination already exists")
    if source.is_file():
        inputs = [source]
    elif source.is_dir():
        inputs = sorted(source.iterdir(), key=lambda v: v.name.casefold())
        if not inputs or any(f.is_symlink() or not f.is_file() or f.suffix.lower() != ".epub"
                             for f in inputs):
            raise ImportFailure("Directory must contain only regular EPUB files")
        if series_title is None:
            raise ImportFailure("A series title is required for multi-volume EPUB imports")
    else:
        raise ImportFailure("Source must be an EPUB or a directory of EPUBs")
    if len(inputs) > 100:
        raise ImportFailure("Too many EPUB volumes")
    stage = Path(tempfile.mkdtemp(prefix=".english-epub-stage-", dir=output.parent if output.parent.exists() else None))
    try:
        input_root = stage / "input"
        name = _folder_name(series_title or source.stem)
        for index, path in enumerate(inputs, 1):
            chapter_folder = input_root / name / _folder_name(path.stem)
            if chapter_folder.exists():
                raise ImportFailure("Duplicate EPUB volume labels")
            result = extract_images(path, chapter_folder)
            if not result["pages"]:
                raise ImportFailure("Empty volume")
        report = import_local(input_root, output, registry, direction="rtl")
        if verify_export(output) != report or report["chapters"] != len(inputs):
            raise ImportFailure("Imported English EPUBs failed Controller export verification")
        return {"status": "verified", "format": "epub", "language": "en", **report}
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import English DRM-free manga EPUB into verified Controller bundle")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--series-title")
    parser.add_argument("--acknowledge-rights", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = import_epubs(args.source, args.output, args.registry, series_title=args.series_title,
                              acknowledge_rights=args.acknowledge_rights)
    except (ImportFailure, OSError, KeyError, ValueError, TypeError) as exc:
        print(f"EPUB import failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
