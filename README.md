# Manga Retriever

**Purpose:** Acquire or import manga files the owner is authorised to retain, verify original image bytes, assemble per-chapter CBZs and produce **local Storage Controller candidate v1** packages. The Retriever is **not** the Manga Library UI or the private Hugging Face data controller.

**Current capabilities (20 November 2026):** Local images/ZIP/CBZ, permitted DRM-free English EPUB and creator-supplied PDF imports; one licensed live-source adapter (Pepper&Carrot Episode 26); fixed-title MangaDex research/local wrappers; a bounded **six-title MangaKatana URL pilot** with resumable local batches. Five previously supported title Chapter 1 CBZs passed ephemeral image verification (246 pages total); the newly added Fairytale-like You title passed a separate real first-chapter test (8 pages), but their English content, full-series coverage and export rights remain unverified. The **public GitHub Actions media allowlist is still restricted to approved licensed material**. There is no arbitrary-site downloader, private HF upload or live Reader integration.

**Start here:** [Project handbook and current architecture](docs/PROJECT_HANDBOOK.md) | [Mandatory AI agent instructions](AGENTS.md) | [Source support matrix](docs/SUPPORTED_SOURCES.md) | [Windows URL download guide](docs/LOCAL_URL_MANGA_DOWNLOAD.md) | [Security](docs/SECURITY.md) | [Roadmap](docs/ROADMAP.md).

> Status rule: a successful metadata or technical chapter-image pilot is **not** proof of a complete, retained English manga download or Controller upload. Check actual archive and run evidence.

## P0 manga request: Acquainted: Encounter Spin-Off

The user's [exact MangaDex title ID](https://mangadex.org/title/90f7c7a6-b759-4afb-b1cb-1af4660df307) has **zero English chapters** in the verified MangaDex feed. An official completed English edition of **50 episodes** exists on [Tapas](https://tapas.io/series/acquainted-encounter-spin-off/info), but [Tapas's in-app offline policy](https://help.tapas.io/hc/en-us/articles/115000415034-Read-offline) does not permit external archive export. Consequently **no CBZ was downloaded or published**. The title is now tracked as highest priority for a legitimate DRM-free English export or rights-holder permission. [Exact audit and next steps](docs/PRIORITY_ACQUAINTED_ENCOUNTER_SPIN_OFF.md).

## Download six NEW requested manga on your Windows computer

Use `Download-New-Manga.cmd "C:\\Manga\\New" pilot` to download one real chapter from each of the six new titles and verify image integrity. After checking source permissions and that their page text is English, run `Download-New-Manga.cmd "C:\\Manga\\New" full` to start verified, resumable 20-chapter local batches. **These new-title downloads never recover previously downloaded ReLIFE, Love So Life, Maid-sama!, Last Game, Onizuka or Kainushi.** The sixth title is *The Fairytale-like You Goes on the Assault* (42 numbered chapters, plus unhandled fractional extras). [One-chapter live check](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44789220759) verified 8 actual image pages. No new series is yet proven to be wholly English or complete, and no copyrighted files are delivered through public GitHub Actions.

## Historical manga recovery, not a missing-title list

**Reconciliation, 26 November 2026:** The Storage Controller's [protected read-only smoke on 20 November](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller/actions/runs/44721448011) verified **five titles already in private canonical storage**: ReLIFE, Love So Life, Last Game, Kaichou wa Maid-sama! and Onizuka-chan and Sawarida-kun (587 chapters, 14,635 pages). Their **30 historical ZIP artefacts are not 30 missing uploads**. Kainushi wa Akuma accounts for the remaining **three selected, partial ZIP artefacts** and was not in that dated five-title snapshot. The private catalogue must be freshly rechecked before inferring any missing chapters. Download eligibility and rights are separate from technical availability.

**Targeted Kainushi preflight (read-only, no media download):** `py -3.12 -m scripts.recover_existing_manga --titles kainushi-wa-akuma --audit-only`. Existing copies require independently checked owner-local retention rights. Explicit `--titles all` remains available for justified backups, but must not be used as a missing-title upload plan.


Previously completed GitHub Actions batches have **33 currently unexpired CBZ artefacts across six requested manga**: ReLIFE, Love So Life (including five extras), Last Game, Kaichou wa Maid-sama!, Onizuka-chan and Sawarida-kun, and partially covered Kainushi wa Akuma. Do **not** repeat huge downloads before inspecting these existing media files; the public metadata registry is not their inventory.

Use [the verified private Windows recovery guide](docs/HISTORICAL_MANGA_ARTIFACT_RECOVERY.md) and launcher `Recover-Existing-Manga.cmd` to download by **exact GitHub artifact ID**, independently inspect actual CBZ images, skip valid existing batches and generate local integrity reports. No new copyright files are uploaded by the recovery utility.

**Workflow safety update (24 November 2026):** Legacy public GitHub Actions jobs that uploaded third-party chapter files, together with their automatic retry jobs, have been [quarantined](docs/LEGACY_MEDIA_WORKFLOW_QUARANTINE.md). Existing historical artefact IDs and private owner-local recovery remain unchanged. The explicitly creator-licensed Pepper&Carrot workflows are unaffected.

Fifteen additional [real original-image chapter checks](.github/workflows/fifteen-manga-image-coverage-checks.yml) are available for five other requested series, covering early, middle and final chapters. These are **ephemeral technical tests**, not retained full-series downloads.

## ManhuaTop: investigated, not yet a working download source

A [real four-title ManhuaTop GitHub Actions investigation](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44803983855) attempted exact series chapter listings through the upstream pinned downloader and **all four failed** with browser/Chromium/network errors (one reported HTTP 403). **No new manga images or archives were downloaded.** The website has not established rights to export copyrighted artwork. See [full source feasibility and next steps](docs/MANHUATOP_VIABILITY_20261121.md). Existing completed manga are explicitly excluded from this source investigation.

## Five-series URL-based chapter download pilot

The [local MangaKatana URL downloader](docs/LOCAL_URL_MANGA_DOWNLOAD.md) now accepts **five exact requested manga URLs** and one to twenty chapters per batch. It uses the independent Manga Downloader CLI, preserves original page bytes, verifies CBZ image integrity and stores files on your own Windows computer. Source pages lacking reliable English labels are **quarantined for manual English-page verification**.

[GitHub Actions technical pilots](.github/workflows/five-real-chapter-download-pilots.yml) attempt one real chapter for each series, but **never publish copyrighted CBZs or pages** to the public repository. Only image-verification JSON reports may be uploaded. This is **not** an end-to-end cloud delivery of the requested manga.

## English manga metadata enrichment (11 titles)

[English Manga Publication Metadata Audit](.github/workflows/publication-metadata.yml) obtains creator/artist credits, English synopsis, genres, publication status and a **cover reference** for 11 source-identity-verified titles. The workflow produces a single `manga-publication-metadata-11-review` artefact with a CSV completeness report and per-title JSON records, for the Storage Controller to review and reconcile without downloading chapters again. The Retriever does **not** download cover artwork or write to Hugging Face. [Full Controller and Library integration handover](docs/METADATA_ENRICHMENT_HANDOVER.md).

When importing existing locally held chapters, pass a reviewed title-matched JSON record using `--metadata-json`; opaque manga/chapter/page IDs and original media bytes remain unchanged.

## English DRM-free manga EPUB import

The new [English EPUB importer](docs/ENGLISH_EPUB_IMPORT.md) accepts owner-supplied **DRM-free English image EPUBs** (one or many volumes), verifies their images, and creates the existing manga Controller candidate and chapter CBZ format without transcoding images. It rejects DRM/encryption metadata and non-English language metadata.

```powershell
py -3.12 -m manga_retriever.epub_import --source "C:\Manga\English Volume.epub" --output "C:\Manga\verified" --registry "C:\Manga\ids.json" --series-title "English Manga" --acknowledge-rights
```

A [successful English-only GitHub Actions EPUB pilot](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44693718612) validated real creator-licensed images, original hashes and the resulting CBZ. It does **not** claim the five requested commercial manga are downloadable or licensed for public artefacts.

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

GitHub Actions CI runs the current synthetic test suite on Windows and Linux, with lint and dependency/security checks. Live-source pilot runs are separate and must be verified using their specific run IDs. See `docs/SOURCE_RESEARCH.md`, `docs/STORAGE_INTEGRATION.md` and `docs/ROADMAP.md`.

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

## M8: first creator-authorised Japanese manga PDF import

The creator of [**Give My Regards to Black Jack**](https://densho810.com/free/) makes an official 13-volume PDF edition available to download. Use the free PDFs obtained directly from that site, install `python -m pip install -e ".[pdf]"`, and run `Import-BlackJack-PDFs.cmd --source "C:\\Manga\\Official-PDFs" --output "C:\\MangaExport\\BlackJack" --registry "C:\\MangaExport\\ids.json" --expected-volumes 13 --official-source`. The source-specific converter validates inputs, rasterises each PDF page into readable PNGs, then produces verified CBZs and a Controller candidate with required **Give My Regards to Black Jack / SHUHO SATO** credits and original PDF SHA-256 provenance. PDF page bytes are transformed rather than preserved. See [PDF manga guide](docs/BLACKJACK_PDF_IMPORT.md) for attribution and reporting obligations.

**This is an offline importer, not an automated PDF downloader.** Direct links, rights reporting, future integration and live website availability have not been verified by an automated adaptor. The original PDF source files are not uploaded to GitHub or Hugging Face.

## ReLIFE: private English full-resolution CBZ pilot

A new [ReLIFE-only Windows workflow](docs/RELIFE_DOWNLOAD.md) uses a user-installed, third-party MangaDex downloader to request **English uploaded originals** (`data`, not `data-saver`). It audits every returned CBZ page for readable image bytes, dimensions and SHA-256. First try `Download-ReLIFE.cmd pilot "C:\Manga\ReLIFE"` for chapters 1–2, then `full` for chapters 1–222 if the pilot works and local use is permitted. No copyrighted pages are downloaded by GitHub Actions or published to this repository. The live download has **not** been verified and chapter completeness is **not** claimed. The 15-volume higher-fidelity official Japanese edition is separately available through BookLive.
