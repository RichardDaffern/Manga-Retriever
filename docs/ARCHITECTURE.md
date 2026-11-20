# Architecture and trust boundaries

**Current system map and status:** Read [the project handbook](PROJECT_HANDBOOK.md) and [source matrix](SUPPORTED_SOURCES.md). The original M1/M2 `manga_retriever.importer` and main CLI are still the **network-free packaging core**; they accept authorised image folders, ZIP/CBZ. ZIP traversal, symlinks, encryption, ratios and quotas are checked; Pillow verifies image MIME and full decode. SHA-256 plus deterministic `pg_` IDs tie page identities to chapter and bytes. Encoded raster bytes are not re-compressed and complete CBZs/Controller candidates are independently reverified before output is published to a new directory.

**Source acquisition now has several bounded implementations:** `manga_retriever.adapters` defines the typed local/Pepper&Carrot acquisition port; `peppercarrot` fetches the one explicitly licensed remote episode; `manga_retriever.relife` and `selected_sources` provide fixed-title opt-in local MangaDex wrappers; `scripts.local_url_manga_download` and `scripts.local_url_manga_bulk` support five exact MangaKatana URLs and resumable 20-chapter local batches; other scripts collect **metadata only**. These are **not** universal URL adapters. A general `discover_series / iter_chapters / stream_pages` remote port remains an architectural proposal, not a complete service. Remote adapters require HTTPS allowlists, DNS/IP SSRF and redirect protection, credentials isolation, limits, rights evidence, rate limiting and checkpoint validation.

**Boundaries:** Retriever owns local packaging. Controller owns private datasets/backups. Reader owns catalogue display/progress/permissions. The Retriever does not write directly into HF or call the Reader. Existing Controller v1 is the reference format, not a promised private-cloud layout.

## Typed source interface

`MangaSourceAdapter.acquire(output, registry)` is implemented by `LocalImportAdapter` and `PepperCarrotEpisode26Adapter`; both produce a verified local export. The webcomic adaptor alone performs network access, using a fixed host/path allowlist, no redirects and bounded retries. It never modifies the Storage Controller or Reader.

## M5 orchestration boundary

`manga_retriever.batch` parses a strictly allowlisted selection and emits JSON matrix jobs. The manually triggered `bulk-manga.yml` runs bounded independent downloads (maximum parallelism 3) using only registered adapters, publishes their **licensed** exports as seven-day GitHub artefacts, then writes small receipt artefacts containing validated source identity, GitHub URL/ID, SHA-256 of the verified CBZ, UTC receipt timestamps and retention expiry. A final serial job collects successes even on partial failure, verifies receipts against the allowlist and updates only `downloaded_manga.json` and `DOWNLOADED_MANGA.md` using bounded optimistic pushes against latest `main`. Missing jobs are listed in `manga_batch_status.json`; a partial batch ends failed without erasing successful artefacts. No user-supplied HTTP URL enters a network fetch.

There is only one authorised production source key, `peppercarrot:26`. Parallelism, multi-source dispatch and large series need newly researched, explicitly approved adapters. The public registry is metadata only and is **not** the personal Manga Reader catalogue.
