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

## M4: verified page-level resume

The authorised Pepper&Carrot episode now checkpoints each successfully downloaded image at `.<output-folder>.checkpoint/` alongside the requested export. On a transient or permanent later-page error, no incomplete CBZ is published. Repeat the **same** command and registry to revalidate and reuse the completed page bytes, fetching only missing or corrupt pages. The official source page and licence are rechecked on every attempt. The checkpoint is removed after a fully verified export is published. **Do not delete or commit the checkpoint while recovering; it contains actual licensed pages.** This is chapter-level only for the sole approved Episode 26; arbitrary manga acquisition remains disabled.

## M5: allowlisted bulk download and metadata registry

Use [**Bulk Manga Download**](.github/workflows/bulk-manga.yml) under GitHub Actions, with selection `peppercarrot:26`. The planner accepts a comma/newline-separated list of **explicitly approved source keys**, rejects unknown URLs, deduplicates requests, and schedules separate capped download jobs (up to 3 in parallel once additional sources are approved). **Only one licensed webcomic episode is approved today; this is a bulk-ready framework, not a catalogue of multiple manga sources.**

Each job verifies complete CBZ/media bytes and posts a short-lived licensed export for 7 days. Successful jobs emit a small validated artefact receipt. A final job aggregates receipts even if another job fails, commits **metadata only** into [downloaded_manga.json](downloaded_manga.json) and [DOWNLOADED_MANGA.md](DOWNLOADED_MANGA.md), and uploads a missing-item status for reruns. It uses a fresh main-branch read and bounded optimistic push retries to avoid registry lost updates. Artefact history does not guarantee availability after deletion or expiry. The repository never retains downloaded pages, CBZs, private rights documents or personal progress.

Local batch planning: `python -m manga_retriever.batch prepare --selection peppercarrot:26`. Future source adapters require separate explicit licensing review and tests before their identifiers may join the production allowlist.

**Live-source verification:** The public Pepper&Carrot website can be temporarily unreachable from GitHub runners. A full live download was verified during M3. M5 synthetic CI verifies the batch planning, receipt and recovery code without making external site health a release gate. To verify live availability, manually run an approved download Action and inspect its complete source-verified artefact.

## M6: Windows download and consolidated ZIP

Use `Download-Manga.cmd` after installing the [GitHub CLI](https://cli.github.com/) and running `gh auth login`, to retrieve the latest **unexpired, approved** licence-authorised GitHub Actions artefact listed in `downloaded_manga.json`. The command re-verifies original export integrity and CBZ SHA-256, and skips existing **valid** copies. Invalid or incomplete copies are **never overwritten automatically**. `Bundle-Manga.cmd` combines independently verified downloads into a local ZIP with a full SHA-256 member manifest. See [step-by-step Windows guide](docs/WINDOWS_RETRIEVAL.md).

**Not a manga-anywhere scraper:** Only the existing approved Pepper&Carrot Episode 26 remains enabled for remote downloading. Creator-authorised Japanese manga [*Give My Regards to Black Jack*](docs/SOURCE_RESEARCH.md) has been identified as a high-priority next source, subject to its more specific attribution, reporting and redistribution terms. Direct PDF download and conversion are not yet implemented.
