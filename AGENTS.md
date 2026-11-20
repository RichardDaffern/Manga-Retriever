# Agent instructions: Manga Retriever

**Applies to this entire repository, including tests, scripts, workflows and documentation.**

This is a **public** source-code repository for manga **acquisition, validation, packaging and local Controller handover**, not the live Manga Library or private manga database.

**Required orientation:** Read [the comprehensive project handbook](docs/PROJECT_HANDBOOK.md), [README](README.md), [source/status guide](docs/SUPPORTED_SOURCES.md), [security policy](docs/SECURITY.md) and the relevant source-specific guide before changing anything. If they conflict, check the *actual code* and latest GitHub Actions evidence, and correct the documentation.

## 1. Repository scope and ownership

- **Work in `RichardDaffern/Manga-Retriever` only.** Use feature branches and focused PRs against canonical `main`.
- Reference but **do not modify** [Manga Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller), [Manga Library](https://github.com/AdityaSreevatsaK/Taiyous-Manga-Library) or the separate Novel Library/Novel Retriever from this assignment.
- Retriever: source investigation, safe local acquisition, unmodified image bytes, archive checks, CBZs, local Controller candidate, source provenance, verification reports.
- Controller: independent candidate validation, private HF dataset/catalogue mutations, backups, conflicts, immutable/revision-aware updates and owner access.
- Reader: library UI, offline reading and progress. **Never have the Retriever write directly to HF or bypass Controller checks.**
- **Never** enable production publishing, a destructive operation, dataset deletion, secret access, new paid services, licence-breaching access or cloud migration without clear owner authorisation. Passing CI alone does not authorise it.

## 2. Non-negotiable requirements

1. **English-first:** The intended personal Manga Library accepts **English manga pages**. The publication's `originalLanguage`, English title, translated synopsis, chapter index and sample image path count are **not proof** that actual page text is English. Preserve a `requiresManualEnglishReview` or equivalent review state when needed.
2. A user may request **a source-specific non-English investigation or download** (such as the exact Korean MangaDex title). Treat this as an explicit, narrowly scoped exception if the media exists and its retrieval is permitted; **never** mislabel or silently import non-English pages into the English catalogue. Preserve source language and isolate the files from English library ingestion.
3. **Rights and terms:** Publicly reachable images, unprotected URLs, reader apps, API access, site "Read offline" buttons, source-language flags or an owner's `--acknowledge-rights` do **not** independently establish publication or archive/export permission. Check the source's explicit licence and individual work rights.
4. **No DRM/paywall/access-control bypass, no CAPTCHA or bot-challenge evasion, no private account scraping.** Respect rate limits, terms, robots and applicable restrictions. Do not add source adapters that require undisclosed credentials or shell injection.
5. **Never publish copyrighted manga images or CBZs through this public repository, public Actions artefacts, PR comments, release assets or logs without independently established redistribution rights.** Use synthetic test fixtures and creator-licensed samples. Private user intent does not make a public artefact private.
6. **No media or secrets committed:** No page images, real rights agreements, personal `ids.json`, HF tokens, user catalogues, EPUB/PDF purchases, private backups or progress. Gitignore is not an access control; inspect PR diffs for leaks.
7. **Source fidelity:** Preserve original image bytes for raster sources, verify dimensions/MIME/full decode and SHA-256. Do not present JPG recompression or MangaDex `data-saver` as original quality. Creator PDF rasterisation is a documented explicit exception.
8. **Identity and completeness:** Preserve existing opaque `mng_`, `ch_`, `pg_` IDs, chapter order and zero-based sequences. List missing/decimal/extra chapters explicitly; never transform a fractional chapter into a main-numbered chapter or declare an incomplete work complete.
9. **Safe filesystem:** Reject symlinks, traversal, ZIP bombs, malformed/untrusted archives, duplicate/colliding paths and oversized files. Never overwrite an existing media export silently. Verify a candidate before atomic publication.
10. **Separate evidence states:** Title metadata, English chapter listing, image manifest, actual image download, validated CBZ, verified complete English series, locally retained/authorised portable package, Controller acceptance, private HF upload and Reader display are **different** statuses. Never promote an earlier state to a later one based on a successful workflow badge.

## 3. Always do this at the start of an assignment

1. Read `AGENTS.md`, the handbook and the file(s) being changed. Read source terms and referenced contracts when relevant. Do **not** rely on an earlier chat summary instead of checking actual repository state.
2. Inspect `main` HEAD, open PRs, branches relevant to the work, last workflow runs and failing job logs. Avoid conflicting duplicate PRs and redundant downloads.
3. Restate the **exact source ID/URL**, edition, chapter range, English/non-English requirement, expected output, rights state and ownership boundary.
4. Classify the work: **metadata investigation**, **technical image probe**, **licensed local acquisition**, **format import**, **Controller contract**, or **infrastructure/CI**. Do not use a metadata-only job as a substitute for an actual user-requested download.
5. Check whether a safe existing adapter already exists before inventing a scraper. Prefer small reusable improvements to the current architecture.
6. Decide which independent source/title tasks can proceed **in parallel** (with bounded concurrency) so that an unrelated blocked source does not stall all investigation.

## 4. Source-specific current facts (dated 20 Nov 2026)

- **Pepper&Carrot Episode 26:** The only explicitly licence-approved remote source in the public bulk allowlist (`peppercarrot:26`). Official six high-resolution English images and CC BY 4.0 attribution. Do not silently expand to other episodes.
- **MangaKatana:** A local URL pilot supports only **six exact pinned title URLs** (Kimi no Iru Machi, Love Hina, Lovely Complex, Mado kara Madoka-chan, Nisekoi and The Fairytale-like You Goes on the Assault). [Five real first-chapter tests](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44755633296) downloaded and verified **246 image pages** in ephemeral CI. All five need actual English-page review; no full series retained or authorised for public media publication. `scripts.local_url_manga_download` and `scripts.local_url_manga_bulk` support local bounded downloads.
- **MangaDex:** Local fixed-title wrappers and metadata probes exist; **not** a general, approved public media export pipeline. Distinguish real MangaDex at-home images from a chapter feed consisting only of external reader links.
- **Acquainted: Encounter Spin-Off (P0):** Exact MangaDex UUID `90f7c7a6-b759-4afb-b1cb-1af4660df307`. [Verified all-language feed](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44761569133) contains **zero chapters**. The original language being Korean does **not** mean MangaDex hosts Korean images. Official Tapas English episodes are app-bound; no authorised portable CBZ source verified. Never claim this title downloaded.
- **Kainushi wa Akuma:** Partially investigated; MangaDex's 45 English feed entries versus 56 alternative listing entries produces **11 unmatched catalogue labels**, not eleven proved absent images. More verification required.
- **Comizy:** Listing observed, no successful verified page downloader. **Weeb Central/Tapas:** no implemented export adaptor.
- **Owner-provided files:** Image ZIP/CBZ, DRM-free English image EPUB and creator-supplied PDF importers exist with format-specific restrictions.
- **Historical results:** The metadata-only `downloaded_manga.json` is **not** a complete owner's private inventory. Verify run ID, media counts, archive checksums and actual current artefact presence before reporting another title as fully downloaded.

For further detail and current links, read [project handbook](docs/PROJECT_HANDBOOK.md), [MangaKatana guide](docs/LOCAL_URL_MANGA_DOWNLOAD.md) and [priority manga investigation](docs/PRIORITY_ACQUAINTED_ENCOUNTER_SPIN_OFF.md).

## 5. Before implementing a new website adapter

- **Pin title identity** using a stable site ID, alias set and edition; reject ambiguous matches, not "closest" titles.
- Investigate rights to download, retain and distribute the *actual media*, not merely to view the page.
- Separate read-only catalogue and at-home image-manifest probing from page downloads.
- Add a **strict allowlist**, HTTPS host/path validation, DNS/IP/SSRF protection, bounded retries, throttling, timeouts and memory/disk budgets; block redirects to untrusted hosts and do not shell out through user strings.
- **Test one chapter with the appropriate permission** before considering a batch: count actual successfully decoded pages, preserve source quality and inspect English page content. Source language fields alone are insufficient.
- Use small resumable batches; limit concurrent jobs and requests; keep per-title failures independent, and verify existing files before skipping them.
- Emit a source/edition/rights provenance record, exact chapter labels, original-versus-compressed status, actual image and CBZ hashes, gaps, output location and permission state. If a stage is unverified, mark it so.
- Do not add unsupported websites to `SUPPORTED_SOURCES.md` under "verified" merely because a third-party downloader lists the domain.

## 6. Controller output contract

- Local output typically contains `chapters/ch_*.cbz`, `controller_candidate/catalogue.json`, `controller_candidate/inventory.json`, `controller_candidate/manifests/ch_*.json`, `controller_candidate/assets/manga/...` and `download_manifest.json`.
- Candidate inventory uses `controllerCandidateVersion: 1`, chapter manifests `schemaVersion: 1` and `mediaKind: manga`. Preserve original image bytes and page-level SHA-256.
- This is a **draft local candidate**, not an HF `data/library.json` production write. Check the live Controller's canonical data contract and independently verify before handing off.
- A `rights.json` owner declaration is **not** independent licence verification. Never mislabel it.
- Keep the private stable-ID registry and any owner rights proof *outside Git*. Back it up before moving/renaming source paths.
- No automatic Controller/Reader repo edits, HF uploads, deletion, backfill or catalogue migration without the owner's specific authorisation.

## 7. Engineering, CI and PR process

- **Environment:** Python 3.12, Windows user workflow, Linux/Windows GitHub Actions. Dependencies are defined in `pyproject.toml`.
- Add **offline deterministic unit tests** for every nontrivial change. Use synthetic Pillow pages, local fake servers or explicit mocked responses. Real copyrighted media must never become a test fixture.
- Run the appropriate gates before merging:

```powershell
py -3.12 -m pip install -e .
py -3.12 -m unittest discover -s tests -v
py -3.12 -m compileall -q manga_retriever tests scripts
py -3.12 -m ruff check manga_retriever tests
```

- Inspect the actual `.github/workflows/ci.yml` for all security and platform steps; a local test is not evidence Windows CI passed.
- Create a named, scoped **feature branch**; commit focused changes; raise a PR explaining source rights, tests, verified media evidence and rollback risks. Address failures until required checks pass.
- The owner has authorised **merging sound, passing, non-destructive PRs without an extra approval prompt**. Do not merge destructive/unapproved production changes or unrelated rewrites under that delegation.
- If a job fails, read its logs and fix the actual cause; do not repeatedly rerun unchanged failing code. Never infer media delivery merely from job status.
- Public Action workflows with historic manga-download names must be inspected before invocation. Some legacy files may contain risky copyrighted media publication; do not treat their existence as authorisation.
- Respect existing branches and unreviewed user changes. Avoid force-push, broad file deletion, stale branch clean-up or protected-branch edits unless explicitly requested.

## 8. Communication, collaboration and future handovers

- Use **British English**, concise progress updates and specific links. Distinguish technical observation from verified fact.
- The user wants **proactive execution**: after finishing a safe approved step, continue to the next actionable step, investigate multiple independent sources in parallel and merge passing PRs as allowed. Do not keep stopping solely for approval of already-authorised work.
- Equally, **do not promise indefinite background work** unless an actual scheduled automation or running GitHub workflow exists. Follow the automation's existing saved task instead of creating duplicates.
- If the source is blocked, **state the precise blocker** (no chapters, no actual images, language unknown, terms forbid export, DRM/app-only access, CI error); proceed with other safe independent work.
- Every handover should include current branch/head SHA/PR, what changed, tests/CI links, source URLs and language, exact expected and verified chapters/pages, media retention/expiry, rights basis, actual owner-controlled file location, open risks and next actions. Do **not** invent local file paths or assert an artefact is still available after expiry.
- **No "100% sure-shot" website claims**: support is per source, edition, chapter, site availability and rights, not universal.

**Final rule: Keep the user's data safe and make all success claims independently verifiable.**
