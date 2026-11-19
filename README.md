# Manga Retriever

**Status: M1 and M2 local starter.** This toolkit imports manga pages you are authorised to possess, validates unmodified source image bytes, creates one CBZ per chapter, and exports a **local Controller v1 candidate**. It does **not** scrape sites, fetch chapters, upload to cloud storage, or connect to the Manga Reader. Source adaptors, resumable remote downloads, bulk actions and production release remain planned.

## Windows quick start

```powershell
py -3.12 -m pip install -e .
py -3.12 -m manga_retriever import --source "C:\Manga\Original Series" --output "C:\MangaExport\MyExport" --registry "C:\MangaExport\ids.json"
py -3.12 -m manga_retriever verify --export "C:\MangaExport\MyExport"
```

`Import-Manga.cmd` and `Verify-Manga.cmd` are alternative Windows entry points. Supported inputs are a chapter folder of images, an individual ZIP/CBZ, or nested `Series/Chapter/pages` and `Series/Chapter.cbz` directories. Recognised pages: PNG, JPEG, WebP and AVIF if the installed Pillow supports it. Output is **never overwritten**. All pages are fully decoded for checks and original encoded bytes are preserved without resizing.

Example output:

```text
MyExport/
  chapters/ch_<id>.cbz       # One verified chapter archive per chapter
  controller_candidate/
    catalogue.json           # MangaEntry v1 shapes, no personal progress
    inventory.json           # Controller candidate v1
    manifests/ch_<id>.json   # ChapterManifest v1, sha256 per page
    assets/manga/mng_<id>/ch_<id>/pg_<id>.png
    rights.json              # Optional, private owner declaration
  download_manifest.json     # Local export summary
```

**Rights:** The optional `--rights-json` file must contain v1 `SourceRights`. This is an owner declaration, *not* independent proof of permission. The Controller's existing `rightsVerified` field means a declaration is present, not that this tool has confirmed licence rights. Without rights evidence the candidate remains a locally inspectable draft. Never publish real media, rights evidence, private catalogues or Actions artefacts publicly.

**Stable IDs:** `--registry` records source paths to opaque series/chapter IDs. Keep and back up this file. Repeat imports of the same path preserve chapter IDs; identical page bytes preserve page IDs. If moving/renaming an input path, maintain the registry mapping before reimporting; automatic path-rename reconciliation is not implemented. Changed page bytes receive a new page ID intentionally.

## Local verification

```powershell
py -3.12 -m unittest discover -s tests -v
py -3.12 -m compileall -q manga_retriever tests
```

GitHub Actions CI runs 17 synthetic tests and a dependency/security check. No live-site test is claimed. See `docs/SOURCE_RESEARCH.md`, `docs/STORAGE_INTEGRATION.md` and `docs/ROADMAP.md`.

## Responsibilities

Manga Retriever produces validated local packages. [Manga Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller) handles owner-controlled private uploads, backups and decisions. [Manga Library](https://github.com/AdityaSreevatsaK/Taiyous-Manga-Library) owns reading UX and progress. No HF writes are enabled in the Storage Controller, and nothing in this project overrides that policy.
