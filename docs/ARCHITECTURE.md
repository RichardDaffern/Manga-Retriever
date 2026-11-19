# Architecture and trust boundaries

M1/M2 implement only `manga_retriever.importer` and CLI. Inputs are local owned/licensed chapter image folders or ZIP/CBZ. Discovery yields a chapter at a time. The ZIP index is checked for traversal, symlinks, encryption, ratio and quotas before reading. Pillow verifies page MIME and full decode. The importer calculates SHA-256 and deterministic `pg_` IDs from chapter ID + page digest, copies **unaltered** bytes to the Controller candidate assets, and writes ordered chapter CBZs. It re-verifies the complete staged export before publishing it to a new output directory.

The separate source-adaptor port is proposed, not implemented: `discover_series(source_ref) -> SeriesMetadata`, `iter_chapters(series_ref, chapter_range)`, `stream_pages(chapter_ref)` with `RightsEvidence`, limits and explicit allowlisted hosts. Remote network use must include DNS/IP SSRF checks, redirects, throttling, checkpoints and only clearly authorised pages. Initial local importer is intentionally network-free.

**Boundaries:** Retriever owns local packaging. Controller owns private datasets/backups. Reader owns catalogue display/progress/permissions. The Retriever does not write directly into HF or call the Reader. Existing Controller v1 is the reference format, not a promised private-cloud layout.

## Typed source interface

`MangaSourceAdapter.acquire(output, registry)` is implemented by `LocalImportAdapter` and `PepperCarrotEpisode26Adapter`; both produce a verified local export. The webcomic adaptor alone performs network access, using a fixed host/path allowlist, no redirects and bounded retries. It never modifies the Storage Controller or Reader.
