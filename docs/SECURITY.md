# Security and media restrictions

The core local importer accepts only trusted local inputs and has no network use. **However, the full repository also contains specific remote adapters and network research probes**, including Pepper&Carrot, fixed-title MangaDex clients and the five-URL MangaKatana local pilot. These **do** introduce HTTP/redirect/SSRF and third-party client risks and must be reviewed separately. See [source matrix](SUPPORTED_SOURCES.md), [agent policy](../AGENTS.md) and [handbook](PROJECT_HANDBOOK.md). ZIP traversal, encrypted members, special entries, case-colliding member paths, suspicious compression ratio and quotas are rejected. Images are verified by Pillow, including magic format and full decode. Budgets are 25 MB/page, 1000 pages/chapter, 500 MB/chapter, 5 GB/import, 10,000 chapters/import, 16,000 pixels/side, 70 million pixels/image.

Input and output symlinks are rejected where checked. Local file race and filesystem capacity remain environmental threats; run imports only in trusted private folders. Outputs are not hosted, uploaded or auto-deleted. Git ignores media, registry and owner rights records. Do not assume Git ignore stops a manually forced git add.

Future network adapters must use explicit HTTPS host allowlists, DNS/rebinding and redirect validation, auth isolation, request/memory budgets, capped exponential backoff and documented publisher permission. Do not enable CI publication of copyrighted pages.

The Pepper&Carrot pilot accepts only the approved official Episode 26 source and six precise HTTPS high-resolution image paths on `www.peppercarrot.com`, with no credentials, arbitrary URLs or redirects. It rejects missing licence links, unrecognised hosts/paths, missing pages, corrupt images and incomplete exports. Retries are limited to selected transient HTTP codes and network failures.

## M5 safe bulk permissions

Bulk jobs take only allowlisted `source:episode` IDs. They cannot request arbitrary hosts/URLs or import personal data into public Actions. The manual workflow grants read-only repository access to download workers, with `contents:write` confined to the serial metadata finaliser. The finaliser records verified short-lived artefact URLs but never commits media. Registry writes use strict receipt validation and bounded retries against fresh `origin/main` to avoid silently overwriting concurrent records. The operational scope is the already verified CC BY 4.0 Episode 26 alone.

## ReLIFE source-specific local-only workflow

The opted-in ReLIFE wrapper invokes a pinned third-party client using `subprocess.run` with an argv list, no shell, no credentials or bypass flags, a fixed MangaDex title ID, English language, and full uploaded-quality CBZ images. It does not run in public CI or expose media through GitHub Actions. The offline CBZ scanner applies path traversal, ZIP encryption/special file, compression ratio, page type/dimensions, member count and byte budgets before recording per-page SHA-256 and a report that never claims series completeness. The third-party client, source availability and end-user local rights are separate trust boundaries; maintainers should review upstream source changes before recommending execution. The user must explicitly acknowledge source permission and must not publish third-party images or scanlations.

## Historical public media workflow quarantine, 24 November 2026

The previously used public GitHub Actions ReLIFE, Love So Life, Last Game/Maid-sama!, Onizuka and Kainushi download jobs uploaded CBZ/media artefacts without independently established redistribution permission. Their historical files may remain downloadable until expiry, but that does not make new public publication acceptable. Their media-producing jobs and related automatic retries are now **quarantined**, not deleted. See [the exact workflow/job register](LEGACY_MEDIA_WORKFLOW_QUARANTINE.md) and its offline regression test.

The approved creator-licensed Pepper&Carrot Episode 26 workflow and JSON-only investigation workflows remain enabled. Recovery of existing eligible files belongs on a private owner-controlled disk; never use this public repository as a surrogate private manga store. Historical runs at older commits may still be rerunnable, so do not revive them as a workaround.
