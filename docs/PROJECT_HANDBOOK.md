# Manga Retriever: project handbook and engineering handover

**Repository:** https://github.com/RichardDaffern/Manga-Retriever  
**Canonical branch:** `main`  
**Owner's environment:** Windows, Python 3.12; GitHub Actions on Windows and Linux  
**Snapshot:** 20 November 2026. Treat current code, CI and source availability as authoritative over this dated snapshot.  
**AI agents:** Read [../AGENTS.md](../AGENTS.md) before making changes.

## 1. Purpose

Manga Retriever is the **acquisition, validation and packaging** component in a private personal manga-library ecosystem. Its purpose is to take manga chapter images or portable files that the owner is authorised to obtain and retain, verify their integrity and provenance, and create **Controller-compatible local candidates and CBZ archives**.

The desired end-to-end user experience is: provide a series URL or owned portable file; identify the exact work and edition; discover accessible chapters and their languages; verify source-specific downloading/export rights; retrieve permitted pages or import an existing file; validate every image and chapter; create ordered CBZs and a Controller candidate; then hand the local result to the separate Storage Controller for inspection and any owner-approved private upload.

**That full experience is a product goal, not a statement of current completion.** The working URL downloader has only five pinned MangaKatana titles, not arbitrary websites; source support and full-series coverage are not guaranteed. The public CI is primarily a code/test and licence-approved pilot environment, not a warehouse for personal manga files.

### The three-repository responsibility split

| Component | Repository | Responsibility | Must not do |
| --- | --- | --- | --- |
| **Retriever (this repo)** | [RichardDaffern/Manga-Retriever](https://github.com/RichardDaffern/Manga-Retriever) | Source investigation, local acquisition/import, original-byte checks, chapter CBZs, portable Controller candidates, integrity reports | Edit the live reader, update the private HF dataset or silently migrate the catalogue |
| **Storage Controller** | [AdityaSreevatsaK/Taiyou-Manga-Storage-Controller](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller) | Review/verify packages, manage stored manga, private uploads/downloads, duplicates, backups, revisions and data migrations | Assume that a Retriever candidate automatically carries upload authority |
| **Manga Library** | [AdityaSreevatsaK/Taiyous-Manga-Library](https://github.com/AdityaSreevatsaK/Taiyous-Manga-Library) | User interface, reading/navigation, offline reader, catalogue presentation and reading progress | Scrape third-party sites or trust unverifiable assets |

The Controller and Reader have their **own** changing contracts. Their source must be re-read before modifying compatibility assumptions. The Retriever's `controller_candidate/catalogue.json` is a **local import candidate**, not evidence that production HF must use that pathname. In the ecosystem, the Controller defines the production `data/library.json` contract; validate that contract in the Controller repository independently before any handover or upload.

### In scope

- English-first, original-image-quality manga acquisition through **source-specific, reviewed** methods.
- Images in local directories, ZIP/CBZ, owner-supplied DRM-free image EPUBs, and supported creator-supplied PDFs.
- Fixed source adaptors, authenticated title/edition identification, chapter pagination, source language checks and integrity audits.
- Repeatable, bounded local downloads with skip-existing and recovery; multiple independent titles in parallel where appropriate.
- Controller candidate v1, CBZ, provenance and verification reports.
- CI for code, synthetic tests and explicitly reusable/licensed source media only.
- Research and source feasibility reports when media retrieval is not possible.

### Explicitly out of scope without a separate approved design

- Unrestricted "paste any website URL" scraping, challenges/CAPTCHA bypass, DRM removal, paywall/login circumvention or unauthorised crawling.
- Committing manga images, private rights files, tokens, personal registry IDs, credentials or catalogue data to this **public** repository.
- Public GitHub Actions media artefacts for copyrighted scanlations without evidenced redistribution permission.
- Direct Hugging Face dataset changes, Storage Controller modifications, Reader modifications, paid purchases or production publishing.
- Treating catalogue listings, successful metadata CI or a licence declaration as proof of successful media download or rights.

## 2. Core principles and product requirements

1. **Exact identity:** Pin a source title ID and edition. A search match, translated title, similarly named sequel or spin-off must not silently substitute for the requested work.
2. **English-only by default:** The owner's personal manga library requires English page text. Language tags on a title are not proof of chapter text language. A specifically requested Korean-language investigation or download may be handled as an **explicit owner exception**, provided the requested media is actually available and retrieval is permitted. Keep any non-English files separate; never relabel them as English or import them into the English catalogue without an explicit policy change.
3. **Permissions before publication:** Public access, an API, a site's "Read offline" option, a rights declaration or a third-party downloader supporting a domain do not themselves prove the copyright owner's permission to export or redistribute the images.
4. **Preserve original image bytes** for supported raster sources, without re-encoding or data-saver conversion. PDF rasterisation is an explicitly documented exception and is not byte-for-byte equivalent to source page images.
5. **No false completeness:** Count *verified real media pages and archives*, compare expected main chapters and extras, record gaps and fail incomplete batches closed.
6. **Repeatability and data protection:** Immutable identifiers, audited files, no blind overwrite, validated skip-existing, atomic publication and deterministic reporting.
7. **Separate the stages:** Discovery and metadata -> source/rights verification -> actual page pilot -> English-content review -> bounded full local acquisition -> verified export -> Controller review -> optional owner-approved storage.
8. **Give the owner accurate updates:** State exactly what worked and what did not. Do not report a catalogue-only run as a downloaded series. Do not leave approved follow-up engineering idle merely to ask for another prompt.

## 3. Current capabilities and evidence

The table deliberately separates implemented code, a successful **limited** pilot, fully retained user data and source-specific legal permission.

| Source/input | Implemented or observed behaviour | What is not proven |
| --- | --- | --- |
| **Owner-provided images / ZIP / CBZ** | Network-free importer creates page-verified CBZ and Controller candidate from local inputs; Python/Windows entry points exist | Rights to possess any individual submitted input, external Controller acceptance |
| **Pepper&Carrot Episode 26** | **Approved live network source:** official six high-resolution English pages, CC BY 4.0 attribution, original-image hashes, chapter CBZ and optional EPUB/ZIP export; checkpoint/recovery | Support for the rest of Pepper&Carrot or arbitrary creator sites |
| **MangaKatana** | Five exact URL allowlists; real Chapter 1 CBZ image tests passed for five manga, **246 decoded image pages** total; bounded local parallel/batch runner | English page text for these files, every chapter/extras, lawful export of all titles, permanent files from public CI |
| **MangaDex** | Exact-ID metadata, English/Korean chapter feed audits, at-home original-image manifest checks, local-only ReLIFE and selected-title downloader wrappers | Generic URL download, universal complete series, publisher-quality scans, public redistribution rights |
| **English image EPUB** | Owner-supplied DRM-free English fixed-layout EPUB importer; real creator-licensed EPUB pilot verified image hashes | DRM removal, validity/availability of requested commercial EPUBs |
| **Creator-supplied PDF** | Local PDF import for *Give My Regards to Black Jack* using approved original PDF files and PDFium rendering | Automatic official PDF download, original JPEG-byte preservation, English-language suitability without verification |
| **Public licensed GitHub artefacts** | Approved key `peppercarrot:26`; bounded manual workflows, receipts, seven-day artefact retrieval and local ZIP bundling | Any arbitrary manga source or lasting cloud backup |
| **Comizy** | Chapter listings explored; image retrieval attempt was not successful | A working adapter or permitted downloadable files |
| **Weeb Central, Tapas, other reading sites** | Read-only research/alternative source listings | Supported source adapter, transferable authorised CBZ or permitted mass download |

**Recorded live MangaKatana Chapter 1 pilot:** [Actions run 44755633296](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44755633296) verified Kimi no Iru Machi **43** pages, Love Hina **81**, Lovely Complex **53**, Mado kara Madoka-chan **14**, and Nisekoi **55**. All were flagged `requiresManualEnglishReview=true`; CI deleted all copyrighted files from its runners and did **not** publish those CBZs as artefacts. Do not describe those five manga as fully downloaded and stored.

**Approved licensed live-media examples:** [English media format pilot](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44686201935) and [DRM-free English EPUB import pilot](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44693718612), both using licensed Pepper&Carrot content. These establish code-path behaviour, not permissions or completeness for unrelated manga.

**Historical manga downloads:** Other named title workflows and earlier user-visible reports may refer to completed ReLIFE, Maid-sama!, Last Game, Love So Life and Onizuka operations. The tracked `downloaded_manga.json` may be empty because it is a registry of a particular approved artefact pipeline, not an inventory of the owner's private files. An agent must locate the exact successful action/artefact or owner's local archive and validate its content before making a present-tense completeness claim.

### Highest-priority outstanding request

**Acquainted: Encounter Spin-Off:** exact MangaDex title `90f7c7a6-b759-4afb-b1cb-1af4660df307`. The title's original language is Korean, but the [all-content-rating Korean/all-language live audit](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44761569133) returned **0 Korean**, **0 English** and **0 chapters across all languages**. Hence MangaDex has *catalogue metadata only*, not image pages. The official English Tapas edition lists 50 episodes, but in-app offline access does not grant portable CBZ/EPUB export. **Status: blocked pending an independently permitted portable edition or rights-holder authorisation.** Do not trigger an empty media job or assume Korean images are present. See [priority handover](PRIORITY_ACQUAINTED_ENCOUNTER_SPIN_OFF.md).

### Other pending title workstreams

| Title | Last established position | Next verification |
| --- | --- | --- |
| **Kainushi wa Akuma** | Partial prior acquisition; 45 MangaDex English feed entries versus 56 alternative entries, with **11 different chapter labels** | Confirm real image coverage, duplicate/subchapter mapping, permitted source and completeness |
| **Kimi no Iru Machi** | MangaKatana Chapter 1: 43 image pages verified | English-page review, chapter-by-chapter retrieval and rights |
| **Love Hina** | MangaKatana Chapter 1: 81 image pages verified | English-page review, chapter-by-chapter retrieval and rights |
| **Lovely Complex** | MangaKatana Chapter 1: 53 image pages verified | English-page review, chapter-by-chapter retrieval and rights |
| **Mado kara Madoka-chan** | MangaKatana Chapter 1: 14 image pages verified | English-page review, chapter-by-chapter retrieval and rights |
| **Nisekoi** | MangaKatana Chapter 1: 55 image pages verified | English-page review, chapter-by-chapter retrieval and rights |

The larger chapter lists in source websites and [feasibility research](REMAINING_MANGA_FEASIBILITY.md) are **indexes**, not fully verified downloads.

## 4. Codebase map

| Path | Responsibility |
| --- | --- |
| `manga_retriever/cli.py`, `__main__.py` | Main CLI: local `import`, `verify`, approved `peppercarrot` |
| `manga_retriever/importer.py` | File/archive validation, page decoding, stable IDs, Controller candidate and CBZ creation |
| `manga_retriever/adapters.py` | Typed acquisition contract and local/Pepper&Carrot adapter implementations |
| `manga_retriever/peppercarrot.py`, `checkpoint.py` | Official six-page licensed source, bounded retries, per-page checkpoint and resumption |
| `manga_retriever/batch.py` | Allowlisted public batch planning, receipts, registry updates and partial failure reporting |
| `manga_retriever/retrieve.py` | Windows `gh` artefact retrieval, integrity rechecks, skip-existing, local ZIP bundling |
| `manga_retriever/relife.py`, `selected_sources.py` | Fixed-title MangaDex local download and independent CBZ audits |
| `scripts/local_url_manga_download.py` | Exact-URL MangaKatana one-to-20-chapter local acquisition, original-image checks and reports |
| `scripts/local_url_manga_bulk.py` | Up to two independent MangaKatana series workers, 20-chapter batches, verified skip and per-title failure isolation |
| `manga_retriever/epub_import.py`, `alternative_formats.py` | DRM-free image EPUB import; approved ZIP/EPUB export formats |
| `manga_retriever/blackjack_pdf.py` | Creator-supplied official PDF volume import and rasterisation |
| `manga_retriever/publication_metadata.py`, `scripts/package_publication_metadata.py` | Public title/author/synopsis/cover-reference metadata and review records |
| `scripts/source_probe_eight.py`, `five_manga_catalogue.py`, `priority_mangadex_title_audit.py`, `acquainted_korean_feed.py` | Fixed-title/URL discovery, English and Korean feeds, chapter labels and image-manifest research |
| `scripts/kainushi_gap_audit.py`, `kainushi_partial.py` | Kainushi English feed/gap/partial work |
| `tests/` | Synthetic offline regression and integrity tests |
| `.github/workflows/` | CI, explicit licensed source jobs, limited live probes, historical recovery and metadata research |
| `Import-Manga.cmd`, `Verify-Manga.cmd`, `Download-Manga.cmd`, `Bundle-Manga.cmd`, `Download-ReLIFE.cmd`, `Import-BlackJack-PDFs.cmd` | Windows launcher scripts |
| `downloaded_manga.json`, `DOWNLOADED_MANGA.md` | Public metadata-only approved artefact registry, **not** the owner's full media inventory |

## 5. Trust boundaries, data formats and identities

The standard local import produces:

```text
NEW_OUTPUT/
  chapters/ch_<opaque-id>.cbz
  controller_candidate/
    catalogue.json
    inventory.json
    manifests/ch_<opaque-id>.json
    assets/manga/mng_<id>/ch_<id>/pg_<id>.<original-extension>
    rights.json                   # optional private owner declaration
  download_manifest.json         # counts, warnings, provenance
```

- Candidate inventory uses `controllerCandidateVersion: 1`; per-chapter manifests use `schemaVersion: 1` and `mediaKind: manga`. See [formats](FORMATS_AND_METADATA.md).
- Preserve opaque `mng_`, `ch_` and `pg_` identities; chapter sequences are zero-based. Page IDs follow content and chapter identity; page-byte changes deliberately alter page IDs.
- `registry` maps local paths to stable identities. **Keep it private and backed up.** A renamed input path may change identity if mappings are not reconciled first.
- Every page needs verified MIME, full successful decode, dimensions, byte size and SHA-256. A chapter CBZ needs ordered pages and complete archive revalidation.
- All local exports go to **new** directories, no silent overwrite. Partial or unsafe output cannot be published as a completed verified export.
- The optional `rights.json` is an owner declaration, **not independent licence verification**; `rightsVerified` must not be overstated.
- Public manga metadata must not contain private user notes, collections, ratings, access credentials or reading progress.
- Packaging only: import candidates must subsequently pass the actual Storage Controller's verifier. **Live Controller acceptance and cloud upload are not established by the Retriever's unit tests.**

### Security and resource controls

Treat site responses, EPUB/ZIP/CBZ/PDF contents, filenames, metadata, chapter numbers, hashes and user URLs as **untrusted input**. Reject traversal, symlink/special files, archive encryption, duplicate or colliding paths, decompression bombs, malformed metadata, unsupported schema versions, inconsistent page counts, corrupt images and unsafe output destinations. The [security specification](SECURITY.md) records current importer budgets, including 25 MB per page, 1,000 pages per chapter, 500 MB per chapter and 5 GB per import. Add tighter source-specific limits where required; do not casually relax them.

For new remote adapters use fixed HTTPS hosts/paths, no redirects across trust boundaries, DNS/IP and SSRF controls, timeouts, bounded retries and rate limits, no shell interpolation and no credentials in logs. Avoid touching production data. Use an explicit rights and source-terms review before CI can publish real media.

## 6. Local workflows (Windows)

Use Python **3.12**. From a trusted checkout of this repository:

```powershell
py -3.12 -m pip install -e .
py -3.12 -m unittest discover -s tests -v
py -3.12 -m compileall -q manga_retriever tests scripts
```

### Import an authorised local manga folder or archive

```powershell
py -3.12 -m manga_retriever import --source "C:\Manga\MyOwnedSeries" --output "C:\MangaExport\NewExport" --registry "C:\MangaPrivate\ids.json"
py -3.12 -m manga_retriever verify --export "C:\MangaExport\NewExport"
```

### Test a single pinned MangaKatana URL locally

Install and independently review the supported [Manga Downloader v25.3.0](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0) command-line executable first. Only after checking the source's terms and local-use permission:

```powershell
py -3.12 -m scripts.local_url_manga_download --url "https://mangakatana.com/manga/nisekoi.553" --chapters 1 --output "C:\Manga\Nisekoi\Pilot-1" --acknowledge-local-rights
```

This is **not a universal domain adapter**; only five pinned URLs are accepted. If the source lacks reliable language labels, inspect the downloaded page text before claiming English.

### Run all five approved URL pilots in parallel

Create a **private, empty directory** first, outside the public repository:

```powershell
New-Item -ItemType Directory -Force "C:\Manga\Downloads"
py -3.12 -m scripts.local_url_manga_bulk --mode pilot --slugs all --workers 2 --output-root "C:\Manga\Downloads" --acknowledge-local-rights
```

If the real pages have been verified as English and local source rights checked, the `--mode full --confirm-english-reviewed` option enables bounded 20-chapter batches with separate per-title failure handling. It **still cannot guarantee** that every chapter is present, correctly translated, accessible or licensed for export. Details: [URL download guide](LOCAL_URL_MANGA_DOWNLOAD.md).

### Other entry points

- Owner-supplied English image EPUB: `py -3.12 -m manga_retriever.epub_import --help`, see [EPUB guide](ENGLISH_EPUB_IMPORT.md). Reject encrypted and non-English files.
- Official owner-supplied *Give My Regards to Black Jack* PDFs: install `-e ".[pdf]"`, use `manga_retriever.blackjack_pdf`, see [PDF guide](BLACKJACK_PDF_IMPORT.md). It is Japanese and outside the default English-catalogue ingestion policy until an authorised English version is verified.
- Licensed Pepper&Carrot Episode 26: `py -3.12 -m manga_retriever peppercarrot --episode 26 --output NEW_OUTPUT --registry PRIVATE_IDS_JSON`.
- Approved public GitHub artefact retrieval: `Download-Manga.cmd` and `Bundle-Manga.cmd` with an authenticated `gh` CLI; only for allowlisted licensed exports. See [Windows retrieval](WINDOWS_RETRIEVAL.md).

No command in this section automatically updates the private HF dataset or live Manga Library.

## 7. GitHub Actions and proof levels

The repository contains **different classes of workflows**. Future agents must inspect the YAML they intend to run, including input defaults, triggers, permissions, outputs, artefact publication and media retention. Historic workflow names alone are not a green light to publish real images.

| Group | Representative workflows | How to interpret their output |
| --- | --- | --- |
| **Quality gates** | `ci.yml` | Python 3.12 Windows/Linux tests, security/dependency checks, lint. A green CI is **code evidence**, not a download |
| **Allowlisted licensed media** | `download-manga.yml`, `bulk-manga.yml`, `english-alternative-formats.yml`, `english-epub-import.yml` | Only an actual successful media artefact, decoded image count, licence and SHA-256 proves a licensed media export |
| **Five-title real image technical probes** | `five-real-chapter-download-pilots.yml` | Successful one-chapter CBZ validation in an **ephemeral** runner; image files are deliberately removed and only JSON may be published |
| **Source research and metadata** | `source-probe-eight.yml`, `five-manga-catalogue.yml`, `publication-metadata.yml`, `parallel-remaining-manga-sources.yml`, `high-priority-mangadex-audit.yml`, `acquainted-korean-feed.yml` | Title IDs, chapter indices, translation feeds, sample image manifests; **no verified media delivery** |
| **Title-specific historic/recovery actions** | `relife-*.yml`, `love-so-life-*.yml`, `maid-sama-source-probe.yml`, `three-manga-*.yml`, `onizuka-recovery-download.yml`, `kainushi-*.yml` | Inspect run ID, current YAML and actual output. Some historic workflows may handle copyrighted image files and **must not be reused for public publication without source rights** |

**Evidence ladder:** (1) Title listed, (2) English chapters indexed, (3) original image URLs manifested, (4) actual page image bytes fetched and validated, (5) archive completeness and English page content verified, (6) licensed portable files stored in the intended place, (7) Controller independently accepted the candidate, (8) Reader shows it correctly. **A workflow passing at step 2 does not imply steps 4 through 8.**

Artefacts on GitHub may expire after **seven days**; see each workflow's retention setting. A GitHub metadata registry is a historical pointer, not a durable download store. For any status report, supply exact workflow run, source, page/chapter counts, output type, retention/expiry and whether the CBZ still exists. Do not claim ongoing asynchronous work unless an actual GitHub job or scheduled automation is running.

### Required quality commands before merging

```powershell
py -3.12 -m unittest discover -s tests -v
py -3.12 -m compileall -q manga_retriever tests scripts
py -3.12 -m ruff check manga_retriever tests
```

Check the actual CI YAML for security-audit commands and platform versions. Run source-independent synthetic tests first; an external site's temporary outage should be tracked separately from deterministic unit failures. Inspect failed job logs and artefacts, not just the workflow badge.

## 8. How to add a new source correctly

1. **Identify exact work**: series URL, stable source ID, editions, author, language, publication status and chapter labels (including fractional extras).
2. **Research access and rights**: official distribution, licence/export terms, original image versus compressed variants, paid/app-only restrictions, host TOS. If source permission is ambiguous, remain in research/metadata-only mode.
3. **Build a read-only probe**: bounded HTTP requests, exact title and chapter-list validation, translated language, image-manifest counts. Avoid downloading artwork when only an index is needed.
4. **Approve a narrow adaptor**: hardcode reviewed allowed hosts or exact titles initially. No arbitrary URL redirects, DRM avoidance, cookies or credentials in CI.
5. **Run a minimal permitted real-image pilot**: one chapter, original quality where available. Verify image decodability, dimensions, per-page hashes and ordered CBZ. Ensure language text really matches the owner's requirements.
6. **Add local download/recovery**: 1–20 chapter batches, bounded concurrency, rate limits, safe retries, atomic publication and resume after errors. Do not mix chapter extras or editions.
7. **Reconcile catalogue and Controller**: preserve opaque identifiers and existing media, enumerate missing/duplicate chapters, validate v1 manifests using the Controller's current code.
8. **Add tests, docs and audit trail**: synthetic malformed inputs, failed network, path attacks, corrupted archives, wrong language, partial batches and no-rights behaviour. Record run IDs and evidence.
9. **Merge only after green checks and review**: focused branch/PR, safe scoped modifications, verified actions and updated status docs. Owner previously authorised merging sound, non-destructive PRs without an additional approval request.
10. **Do not overstate delivery**: retain the exact distinction among metadata, ephemeral image test, locally kept media and private Controller upload.

A third-party downloader advertising hundreds of domains is only a **compatibility lead**. Each new website still needs its own tests and rights assessment; never advertise a 100% guaranteed website or source-independent success.

## 9. Maintenance, status and known gaps

**P0**: Acquainted: Encounter Spin-Off permitted portable source; MangaDex hosts zero chapters. Do not confuse title metadata's `originalLanguage=ko` with hosted Korean scans.

**P1**: Establish English page content, source terms and actual full chapter coverage of the five successful MangaKatana one-chapter pilots, then support safe locally retained completion where permitted.

**P1**: Kainushi wa Akuma gap reconciliation: MangaDex 45 versus alternate index 56; [source research](PARALLEL_ENGLISH_MANGA_SOURCE_RESEARCH.md) and Kainushi chapter-label workflow. Not eleven *proven missing source image files*, just eleven unmatched labels in a particular catalogue comparison.

**P1**: Independent end-to-end Controller v1 acceptance and first verified owner-approved local import, with stable-ID reconciliation and backup. Never infer a Controller upload occurred.

**P2**: Cohesive source registry and rights policy; reusable external-source interface; explicit permission-aware URL validation; stronger live English-language evidence and run receipts.

**P2**: UI/controller integration is separate work; coordinate through documented contract handovers rather than editing those repos directly.

**Documentation consistency:** Historical milestone sections across this repository may describe earlier capabilities; introductory status in the README, source matrix, architecture, security and roadmap is maintained alongside this handbook. **Use this handbook, current `AGENTS.md`, actual code, latest successful run IDs and more recent title-specific documents for present capability.** Treat stale "not implemented" lines as historical context, not the sole status source; update those documents when changing affected features.

### Decision log and documentation precedence

1. Safety/security and explicit owner authorisation, including public-repository rules.
2. Current repository code and workflow definitions on `main`, independent Controller/Reader contracts.
3. Latest reproducible CI runs and verifiable source artefacts.
4. This handbook and [AGENTS.md](../AGENTS.md).
5. Specific current source investigations and user-approved decisions.
6. Older milestone/roadmap descriptions as historical background only.

If evidence conflicts, **investigate and document the discrepancy** before changing data or declaring success.

## 10. AI agent handover checklist

Before ending a session or PR, record:

- [ ] GitHub repository/branch/head SHA, PR link, base branch and merged/not merged state.
- [ ] The exact request and priority, including title ID, language, source URL and permission assumptions.
- [ ] Which feature exists versus remains a proposal or experiment.
- [ ] Which live CI/download runs actually completed, with links and conclusion.
- [ ] Exact expected versus verified chapter and image counts, extras/gaps and English validation status.
- [ ] Whether actual media is **only ephemeral**, **locally retained**, **in a licence-approved artefact**, **passed to Controller**, or **uploaded to private HF**.
- [ ] Real artefact name/size/checksum/expiry if applicable; no invented links or output locations.
- [ ] Rights/terms evidence and the unresolved permissions, if any.
- [ ] Tests run and failures investigated, on Windows/Linux/security where applicable.
- [ ] File/format contract changes and ID-preservation/migration notes.
- [ ] Remaining actionable steps in priority order, separate from genuine external blockers.
- [ ] A concise owner-facing status with truthful completion terminology.

**Success is an evidenced, independently verifiable result, not the absence of a failed CI badge.**
