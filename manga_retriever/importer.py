"""Strict local import and original-byte CBZ/controller candidate export.

Controller candidate layout and ID rules mirror Taiyou-Manga-Storage-Controller v1.
Only local, explicitly supplied files are read. No network access is performed.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import secrets
import shutil
import stat
import tempfile
import warnings
import zipfile
from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from PIL import Image, ImageFile

Image.MAX_IMAGE_PIXELS = 70_000_000
ImageFile.LOAD_TRUNCATED_IMAGES = False
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".avif": "image/avif"}
PIL_MIME = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp", "AVIF": "image/avif"}
MAX_IMAGE = 25_000_000
MAX_CHAPTER = 500_000_000
MAX_TOTAL = 5_000_000_000
MAX_PAGES = 1000
MAX_CHAPTERS = 10000


class ImportFailure(ValueError):
    """Unsafe, incomplete or incompatible input. No output is published."""


@dataclass(frozen=True)
class ChapterInput:
    key: str
    series_key: str
    title: str
    label: str
    volume: str | None
    location: Path
    archived: bool


def natural_key(value: str) -> list[tuple[int, object]]:
    return [(1, int(piece)) if piece.isdigit() else (0, piece.casefold())
            for piece in re.split(r"(\d+)", value)]


def _regular(path: Path, root: Path) -> None:
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ImportFailure(f"Symlink or escaped input: {path.name}")
    if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise ImportFailure(f"Not a regular file: {path.name}")


def _safe_member(name: str) -> None:
    parts = name.split("/")
    if (not name or len(name) > 240 or "\\" in name or "%" in name or "\x00" in name
            or ":" in name or len(parts) > 10 or any(p in ("", ".", "..") for p in parts)
            or PurePosixPath(name).is_absolute()):
        raise ImportFailure("Unsafe ZIP/CBZ entry path")


def _file_chunks(path: Path) -> Iterator[tuple[str, bytes]]:
    root = path
    names: set[str] = set()
    files = sorted(path.iterdir(), key=lambda x: natural_key(x.name))
    if not 1 <= len(files) <= MAX_PAGES:
        raise ImportFailure("Folder is empty or exceeds page limit")
    total = 0
    for f in files:
        _regular(f, root)
        if f.suffix.lower() not in MIME or f.name.casefold() in names:
            raise ImportFailure("Unsupported or duplicate page file")
        names.add(f.name.casefold())
        if not 1 <= f.stat().st_size <= MAX_IMAGE:
            raise ImportFailure("Page file exceeds limit")
        total += f.stat().st_size
        if total > MAX_CHAPTER:
            raise ImportFailure("Chapter exceeds byte limit")
    for f in files:
        with f.open("rb") as handle:
            content = handle.read(MAX_IMAGE + 1)
        if not 1 <= len(content) <= MAX_IMAGE:
            raise ImportFailure("Page changed or exceeds limit during read")
        yield f.name, content


def _archive_chunks(path: Path) -> Iterator[tuple[str, bytes]]:
    if path.stat().st_size > MAX_CHAPTER:
        raise ImportFailure("Compressed archive exceeds quota")
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            if not 1 <= len(entries) <= MAX_PAGES + 100:
                raise ImportFailure("Archive entry limit exceeded")
            found: set[str] = set()
            images: list[zipfile.ZipInfo] = []
            total = 0
            for member in entries:
                _safe_member(member.filename[:-1] if member.is_dir() else member.filename)
                if member.is_dir():
                    continue
                mode = member.external_attr >> 16
                if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                    raise ImportFailure("Archive contains symlink or special file")
                if member.flag_bits & 1:
                    raise ImportFailure("Encrypted archive unsupported")
                name = member.filename.casefold()
                if name in found:
                    raise ImportFailure("Duplicate archive member")
                found.add(name)
                if Path(name).suffix not in MIME:
                    raise ImportFailure("Non-image archive member")
                if not 1 <= member.file_size <= MAX_IMAGE:
                    raise ImportFailure("Archive member exceeds page quota")
                if member.file_size > max(member.compress_size, 1) * 100:
                    raise ImportFailure("Suspicious ZIP compression ratio")
                total += member.file_size
                if total > MAX_CHAPTER:
                    raise ImportFailure("Uncompressed chapter quota exceeded")
                images.append(member)
            if not 1 <= len(images) <= MAX_PAGES:
                raise ImportFailure("Archive has no pages or too many pages")
            for member in sorted(images, key=lambda x: natural_key(x.filename)):
                with archive.open(member) as handle:
                    content = handle.read(MAX_IMAGE + 1)
                if len(content) != member.file_size:
                    raise ImportFailure("Archive page size differs from metadata")
                yield member.filename, content
    except (zipfile.BadZipFile, RuntimeError, EOFError, OSError) as error:
        raise ImportFailure("Corrupt or unreadable CBZ/ZIP") from error


def _validate_image(data: bytes, filename: str) -> dict:
    extension = Path(filename).suffix.lower()
    if extension not in MIME or not 1 <= len(data) <= MAX_IMAGE:
        raise ImportFailure("Unsupported page type or byte size")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as probe:
                actual = PIL_MIME.get(probe.format or "")
                if actual != MIME[extension]:
                    raise ImportFailure("Page MIME differs from signature")
                width, height = probe.size
                if not (1 <= width <= 16000 and 1 <= height <= 16000 and width * height <= 70000000):
                    raise ImportFailure("Image dimensions exceed quota")
                probe.verify()
            with Image.open(io.BytesIO(data)) as decoded:
                decoded.load()
    except (OSError, SyntaxError, ValueError, Image.DecompressionBombWarning,
            Image.DecompressionBombError) as error:
        if isinstance(error, ImportFailure):
            raise
        raise ImportFailure(f"Invalid or truncated page: {filename}") from error
    return {"mimeType": actual, "width": width, "height": height,
            "byteSize": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def _walk(root: Path) -> Iterator[Path]:
    stack = [root]
    while stack:
        folder = stack.pop()
        children = sorted(folder.iterdir(), key=lambda x: natural_key(x.name))
        subfolders = []
        for child in children:
            if child.is_symlink() or not child.resolve().is_relative_to(root.resolve()):
                raise ImportFailure("Linked or escaped input forbidden")
            if child.is_dir():
                subfolders.append(child)
        stack.extend(reversed(subfolders))
        yield folder


def discover(source: Path) -> Iterator[ChapterInput]:
    if source.is_symlink() or not source.exists():
        raise ImportFailure("Source missing or symlinked")
    if source.is_file():
        if source.suffix.lower() not in (".cbz", ".zip"):
            raise ImportFailure("Only ZIP/CBZ archives accepted as files")
        yield ChapterInput(source.name, source.name, source.stem, "Chapter 1", None, source, True)
        return
    found = 0
    for folder in _walk(source):
        entries = list(folder.iterdir())
        page_files = [x for x in entries if x.is_file() and x.suffix.lower() in MIME]
        if page_files:
            relative = folder.relative_to(source)
            key = relative.as_posix()
            series_key = relative.parts[0] if relative.parts else "."
            title = source.name if series_key == "." else series_key
            label = "Chapter 1" if relative == Path(".") else relative.parts[-1]
            volume = relative.parts[-2] if len(relative.parts) >= 3 else None
            found += 1
            yield ChapterInput(key, series_key, title, label, volume, folder, False)
        for archive in sorted(entries, key=lambda x: natural_key(x.name)):
            if archive.is_file() and archive.suffix.lower() in (".cbz", ".zip"):
                relative = archive.relative_to(source)
                series_key = relative.parts[0] if len(relative.parts) > 1 else "."
                title = source.name if series_key == "." else series_key
                volume = relative.parts[-2] if len(relative.parts) >= 3 else None
                found += 1
                yield ChapterInput(relative.as_posix(), series_key, title, archive.stem,
                                   volume, archive, True)
    if not found:
        raise ImportFailure("No chapter folders or CBZ/ZIP archives found")


def _new_id(prefix: str) -> str:
    return prefix + "_" + secrets.token_hex(12)


def _id_for(ids: dict[str, str], key: str, prefix: str) -> str:
    if key not in ids:
        ids[key] = _new_id(prefix)
    value = ids[key]
    if not re.fullmatch(rf"{prefix}_[a-zA-Z0-9_-]{{8,64}}", value):
        raise ImportFailure("Invalid saved identity")
    return value


def _page_id(chapter_id: str, checksum: str) -> str:
    return "pg_" + hashlib.sha256(f"{chapter_id}:{checksum}".encode("ascii")).hexdigest()[:24]


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def _read_rights(path: Path | None) -> dict | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or set(data) != {"schemaVersion", "sourceType", "title",
            "permissionEvidence", "attribution", "recordedAt"}
            or data["schemaVersion"] != 1
            or data["sourceType"] not in ("original", "owned", "licensed")):
        raise ImportFailure("Invalid SourceRights v1 evidence")
    for field, max_len in (("title", 180), ("permissionEvidence", 400), ("attribution", 400)):
        item = data[field]
        if not isinstance(item, str) or not item.strip() or len(item) > max_len:
            raise ImportFailure("Invalid rights field " + field)
    if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", data["recordedAt"]):
        raise ImportFailure("Invalid UTC rights timestamp")
    return data


@contextmanager
def _locked_registry(path: Path) -> Iterator[dict[str, str]]:
    if path.is_symlink():
        raise ImportFailure("Registry symlinks prohibited")
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise ImportFailure("Import already in progress or stale registry lock") from error
    try:
        os.close(fd)
        ids = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        if (not isinstance(ids, dict)
                or any(not isinstance(k, str) or not k.startswith(("series:", "chapter:"))
                       or not isinstance(v, str) for k, v in ids.items())
                or len(set(ids.values())) != len(ids)):
            raise ImportFailure("Invalid identity registry")
        yield ids
        fd, filename = tempfile.mkstemp(prefix=".manga-ids-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                json.dump(ids, output, indent=2, sort_keys=True)
                output.flush()
                os.fsync(output.fileno())
            os.replace(filename, path)
        finally:
            Path(filename).unlink(missing_ok=True)
    finally:
        lock.unlink(missing_ok=True)


def import_local(source: Path, output: Path, state: Path, *, rights_path: Path | None = None,
                 direction: str = "rtl") -> dict:
    """Build a new, verified candidate bundle and chapter CBZ set, never overwrite."""
    if direction not in {"rtl", "ltr", "vertical"}:
        raise ImportFailure("Unsupported reading direction")
    if source.is_dir() and (output.resolve().is_relative_to(source.resolve())
                            or state.resolve().is_relative_to(source.resolve())):
        raise ImportFailure("Output and identity registry must live outside the source")
    if output.exists() or output.is_symlink():
        raise ImportFailure("Destination already exists. Refusing to replace data")
    rights = _read_rights(rights_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with _locked_registry(state) as ids:
        stage = Path(tempfile.mkdtemp(prefix=".manga-retriever-", dir=output.parent))
        try:
            records = defaultdict(list)
            titles: dict[str, str] = {}
            warnings_list: list[str] = []
            chapters_total = 0
            pages_total = 0
            byte_total = 0
            for chapter in discover(source):
                chapters_total += 1
                if chapters_total > MAX_CHAPTERS:
                    raise ImportFailure("Too many chapters")
                series_id = _id_for(ids, "series:" + chapter.series_key, "mng")
                chapter_id = _id_for(ids, "chapter:" + chapter.key, "ch")
                titles[series_id] = chapter.title
                page_source = _archive_chunks(chapter.location) if chapter.archived else _file_chunks(chapter.location)
                pages: list[dict] = []
                hashes: set[str] = set()
                indexes = []
                cbz = stage / "chapters" / (chapter_id + ".cbz")
                cbz.parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(cbz, "w", compression=zipfile.ZIP_DEFLATED) as writer:
                    for name, data in page_source:
                        checked = _validate_image(data, name)
                        byte_total += len(data)
                        if byte_total > MAX_TOTAL:
                            raise ImportFailure("Entire import exceeds total size quota")
                        if checked["sha256"] in hashes:
                            raise ImportFailure("Exact duplicate page within chapter")
                        hashes.add(checked["sha256"])
                        match = re.search(r"(\d+)$", Path(name).stem)
                        indexes.append(int(match.group(1)) if match else None)
                        page_id = _page_id(chapter_id, checked["sha256"])
                        extension = Path(name).suffix.lower()
                        asset_path = f"manga/{series_id}/{chapter_id}/{page_id}{extension}"
                        page = {"id": page_id, "assetPath": asset_path, **checked}
                        pages.append(page)
                        dest = stage / "controller_candidate" / "assets" / asset_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_bytes(data)
                        writer.writestr(f"{len(pages):04d}{extension}", data)
                if not pages:
                    raise ImportFailure("Chapter has no pages")
                if all(i is not None for i in indexes):
                    nums = [int(i) for i in indexes if i is not None]
                    if len(set(nums)) != len(nums):
                        warnings_list.append(f"Repeated page indices in {chapter.key}")
                    elif sorted(nums) != list(range(min(nums), max(nums) + 1)):
                        warnings_list.append(f"Missing numbered page(s) in {chapter.key}")
                _write_json(stage / "controller_candidate" / "manifests" / (chapter_id + ".json"),
                            {"schemaVersion": 1, "mediaKind": "manga", "chapterId": chapter_id,
                             "pages": pages})
                records[series_id].append({"id": chapter_id, "label": chapter.label,
                                           "volume": chapter.volume, "pageCount": len(pages)})
                pages_total += len(pages)
            if not chapters_total:
                raise ImportFailure("No chapters found")
            catalogue = []
            for sid, chapters in sorted(records.items(), key=lambda pair: titles[pair[0]].casefold()):
                chapters.sort(key=lambda c: natural_key((c["volume"] or "") + "/" + c["label"]))
                chapter_records = []
                for sequence, item in enumerate(chapters):
                    chapter_records.append({k: v for k, v in {**item, "sequence": sequence}.items()
                                            if v is not None})
                catalogue.append({"kind": "manga", "id": sid, "title": titles[sid],
                                  "aliases": [], "creators": [], "tags": [],
                                  "publicationStatus": "unknown", "direction": direction,
                                  "chapters": chapter_records})
            bundle = stage / "controller_candidate"
            _write_json(bundle / "catalogue.json", catalogue)
            inventory = {"controllerCandidateVersion": 1, "mediaKind": "manga",
                         "state": "local-draft-not-approved-persisted-schema",
                         "series": len(catalogue), "chapters": chapters_total,
                         "pages": pages_total, "warnings": warnings_list,
                         "rightsVerified": rights is not None}
            _write_json(bundle / "inventory.json", inventory)
            if rights is not None:
                _write_json(bundle / "rights.json", rights)
            _write_json(stage / "download_manifest.json", {"schemaVersion": 1,
                        "sourceType": "authorised-local-import", "publicationStatus": "unknown",
                        "rightsDeclared": rights is not None, "series": len(catalogue),
                        "chapters": chapters_total, "pages": pages_total,
                        "sha256Format": "lowercase", "warnings": warnings_list})
            result = verify_export(stage)
            if output.exists() or output.is_symlink():
                raise ImportFailure("Destination appeared during import; refusing overwrite")
            stage.rename(output)
            return result
        finally:
            if stage.exists():
                shutil.rmtree(stage)


def verify_export(export: Path) -> dict:
    """Rehash every original image and verify CBZ bytes against the controller candidate."""
    root = export / "controller_candidate"
    if export.is_symlink() or root.is_symlink() or any(p.is_symlink() for p in root.rglob("*")):
        raise ImportFailure("Symbolic links in export are prohibited")
    catalogue = json.loads((root / "catalogue.json").read_text(encoding="utf-8"))
    inventory = json.loads((root / "inventory.json").read_text(encoding="utf-8"))
    if inventory.get("controllerCandidateVersion") != 1 or inventory.get("mediaKind") != "manga":
        raise ImportFailure("Incompatible controller candidate version")
    paths: set[str] = set()
    chapter_ids: set[str] = set()
    pages_count = 0
    for entry in catalogue:
        for chapter in entry["chapters"]:
            cid = chapter["id"]
            if cid in chapter_ids:
                raise ImportFailure("Duplicate chapter ID")
            chapter_ids.add(cid)
            manifest = json.loads((root / "manifests" / (cid + ".json")).read_text(encoding="utf-8"))
            if (manifest.get("chapterId") != cid or manifest.get("schemaVersion") != 1
                    or manifest.get("mediaKind") != "manga"
                    or chapter["pageCount"] != len(manifest["pages"])):
                raise ImportFailure("Chapter manifest invalid or incomplete")
            cbz_path = export / "chapters" / (cid + ".cbz")
            with zipfile.ZipFile(cbz_path) as cbz:
                cbz_members = cbz.namelist()
                if len(cbz_members) != len(manifest["pages"]):
                    raise ImportFailure("CBZ page count mismatch")
                for i, page in enumerate(manifest["pages"]):
                    asset_path = page["assetPath"]
                    if not re.fullmatch(r"manga/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+/[A-Za-z0-9_-]+\.(png|jpg|jpeg|webp|avif)", asset_path):
                        raise ImportFailure("Unsafe asset path in candidate")
                    if not asset_path.startswith(f'manga/{entry["id"]}/{cid}/') or asset_path in paths:
                        raise ImportFailure("Wrong series ownership or duplicate asset")
                    paths.add(asset_path)
                    data = (root / "assets" / asset_path).read_bytes()
                    checked = _validate_image(data, asset_path)
                    if any(checked[k] != page[k] for k in ("mimeType", "sha256", "width", "height", "byteSize")):
                        raise ImportFailure("Image corruption or manifest inconsistency")
                    with cbz.open(cbz_members[i]) as reader:
                        if reader.read(MAX_IMAGE + 1) != data:
                            raise ImportFailure("CBZ and candidate image bytes differ")
                    pages_count += 1
    actual = {p.relative_to(root / "assets").as_posix() for p in (root / "assets").rglob("*") if p.is_file()}
    if actual != paths:
        raise ImportFailure("Unreferenced or missing images in candidate")
    if (inventory.get("series"), inventory.get("chapters"), inventory.get("pages")) != (
            len(catalogue), len(chapter_ids), pages_count):
        raise ImportFailure("Inventory totals differ from manifest contents")
    return {"series": len(catalogue), "chapters": len(chapter_ids), "pages": pages_count}
