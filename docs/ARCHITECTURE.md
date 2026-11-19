# Architecture and trust boundaries

M1/M2 implement only `manga_retriever.importer` and CLI. Inputs are local owned/licensed chapter image folders or ZIP/CBZ. Discovery yields a chapter at a time. The ZIP index is checked for traversal, symlinks, encryption, ratio and quotas before reading. Pillow verifies page MIME and full decode. The importer calculates SHA-256 and deterministic `pg_` IDs from chapter ID + page digest, copies **unaltered** bytes to the Controller candidate assets, and writes ordered chapter CBZs. It re-verifies the complete staged export before publishing it to a new output directory.

The separate source-adaptor port is proposed, not implemented: `discover_series(source_ref) -> SeriesMetadata`, `iter_chapters(series_ref, chapter_range)`, `stream_pages(chapter_ref)` with `RightsEvidence`, limits and explicit allowlisted hosts. Remote network use must include DNS/IP SSRF checks, redirects, throttling, checkpoints and only clearly authorised pages. Initial local importer is intentionally network-free.

**Boundaries:** Retriever owns local packaging. Controller owns private datasets/backups. Reader owns catalogue display/progress/permissions. The Retriever does not write directly into HF or call the Reader. Existing Controller v1 is the reference format, not a promised private-cloud layout.

## Typed source interface

`MangaSourceAdapter.acquire(output, registry)` is implemented by `LocalImportAdapter` and `PepperCarrotEpisode26Adapter`; both produce a verified local export. The webcomic adaptor alone performs network access, using a fixed host/path allowlist, no redirects and bounded retries. It never modifies the Storage Controller or Reader.

## M5 orchestration boundary

`manga_retriever.batch` parses a strictly allowlisted selection and emits JSON matrix jobs. The manually triggered `bulk-manga.yml` runs bounded independent downloads (maximum parallelism 3) using only registered adapters, publishes their **licensed** exports as seven-day GitHub artefacts, then writes small receipt artefacts containing validated source identity, GitHub URL/ID, SHA-256 of the verified CBZ, UTC receipt timestamps and retention expiry. A final serial job collects successes even on partial failure, verifies receipts against the allowlist and updates only `downloaded_manga.json` and `DOWNLOADED_MANGA.md` using bounded optimistic pushes against latest `main`. Missing jobs are listed in `manga_batch_status.json`; a partial batch ends failed without erasing successful artefacts. No user-supplied HTTP URL enters a network fetch.

There is only one authorised production source key, `peppercarrot:26`. Parallelism, multi-source dispatch and large series need newly researched, explicitly approved adapters. The public registry is metadata only and is **not** the personal Manga Reader catalogue.
