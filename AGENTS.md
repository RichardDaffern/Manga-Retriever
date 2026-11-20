# Agent working agreement

- Scope: RichardDaffern/Manga-Retriever only. Reference repositories, never modify the Reader, Controller or Novel Retriever from this project.
- Start with an audit of current branches/PRs/CI, the local README and all docs. Use feature branches and PRs.
- Respect licensing and each site's explicit terms. A publicly accessible page/API does not establish downloadable rights. No DRM bypass, access-control circumvention, anti-bot evasion, or remote downloads to public CI without express permission.
- Never commit copyrighted manga, actual rights records, personal catalogues or tokens. Synthetic tests only.
- Build original-byte-preserving verified CBZs and Controller-candidate bundles; never mark incomplete inputs complete. Fail closed on unsupported schema versions and unsafe archives/URLs.
- Maintain immutable mng_/ch_/pg_ IDs and zero-based chapter sequences, compatible with Reader/Controller v1. Source path registry mapping is backed up privately.
- Do not activate cloud uploads, private dataset access, destructive actions or production release without owner approval.
- Document implemented vs proposed capabilities honestly. No unverified CI or integration claims.

## English-only manga acquisition (owner requirement, 20 November 2026)

- **All manga retrieved for this library must be in English.** Do not fetch Japanese originals, multilingual bundles containing Japanese chapters, or translate Japanese images as a substitute.
- Treat a series chapter list (including a full MangaKatana chapter index) as **metadata-only**, not as verified English artwork or a download result. Any title lacking independently verified English pages must remain unverified.
- For downloads require the selected edition to be English, a permitted retrieval/export mechanism, complete expected pages and page-integrity verification, without DRM, account or challenge bypass. Clearly distinguish **official application offline reading** from portable CBZ/PDF downloads.
- Do not publish copyrighted English manga through public GitHub Actions artefacts without established redistribution rights. Never assert a successful download based solely on a successful catalogue workflow.
- Before declaring any title downloaded, verify that the job published real image-containing CBZs/PDFs and report chapter/page counts and artefact expiry.
