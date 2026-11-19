# Manga Retriever

**Status: M1/M2 complete; M3 first authorised live-source adapter available for one explicitly licensed webcomic episode.** This toolkit imports manga pages you are authorised to possess, validates unmodified source image bytes, creates one CBZ per chapter, and exports a **local Controller v1 candidate**. It does **not** enable general manga-site scraping, arbitrary chapter URLs, cloud storage or Manga Reader integration. The initial Pepper&Carrot adapter supports only the creator-published high-resolution English pages of episode 26 under CC BY 4.0; larger source coverage, bulk resumable downloads and production release remain planned.

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

## Download the first authorised webcomic source

The official [Pepper&Carrot Episode 26 source page](https://www.peppercarrot.com/en/webcomic-sources/ep26_Books-Are-Great.html) publishes six high-resolution English pages under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) with attribution. The adapter validates the official licence link, expected six page URLs and source host, blocks redirects, retries only transient errors, and records page-level source URLs plus SHA-256 in `download_manifest.json`. It preserves image bytes and credits contributors through the official episode credit page. This **webcomic** is not being represented as Japanese manga.

```powershell
py -3.12 -m manga_retriever peppercarrot --episode 26 --output "C:\MangaExport\Pepper26" --registry "C:\MangaExport\ids.json"
py -3.12 -m manga_retriever verify --export "C:\MangaExport\Pepper26"
```

Alternatively, use [Single Manga Download](.github/workflows/download-manga.yml) under GitHub Actions. The workflow publishes only this licensed work, with its attribution, as a short-lived artefact. A metadata-only API does not authorise general-purpose manga archiving. Live success must be verified from a completed Action; offline tests do not prove site availability.

## Local verification

```powershell
py -3.12 -m unittest discover -s tests -v
py -3.12 -m compileall -q manga_retriever tests
```

GitHub Actions CI runs 25 synthetic tests and a dependency/security check. No live-site test is claimed. See `docs/SOURCE_RESEARCH.md`, `docs/STORAGE_INTEGRATION.md` and `docs/ROADMAP.md`.

## Responsibilities

Manga Retriever produces validated local packages. [Manga Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller) handles owner-controlled private uploads, backups and decisions. [Manga Library](https://github.com/AdityaSreevatsaK/Taiyous-Manga-Library) owns reading UX and progress. No HF writes are enabled in the Storage Controller, and nothing in this project overrides that policy.
