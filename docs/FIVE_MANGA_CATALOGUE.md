# Five remaining manga: read-only chapter catalogue checks

Research date: **20 November 2026**. This is deliberately **not a media downloader**.

## Verified engineering route

The third-party [Manga Downloader](https://github.com/elboletaire/manga-downloader) release
[v25.3.0](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0)
documents support for MangaKatana (site tested 16 November 2026) and provides
`manga-downloader list --json [series-url]`. That command **lists chapters without
downloading chapter images**. The metadata-only GitHub Actions workflow
[`five-manga-catalogue.yml`](../.github/workflows/five-manga-catalogue.yml)
tests the following **fixed** series URLs independently:

| Manga | Candidate MangaKatana listing | Main chapters to reconcile |
| --- | --- | ---: |
| Kimi no Iru Machi | [Listing](https://mangakatana.com/manga/kimi-no-iru-machi.2162) | 261 |
| Love Hina | [Listing](https://mangakatana.com/manga/love-hina.4545) | 120 |
| Lovely Complex | [Listing](https://mangakatana.com/manga/lovely-complex.6103) | 66 |
| Mado kara Madoka-chan | [Listing](https://mangakatana.com/manga/mado-kara-madoka-chan.21642) | 74, plus fractional afterword |
| Nisekoi | [Listing](https://mangakatana.com/manga/nisekoi.553) | 229 |

**These are provisional expectations from external indices, not established coverage
or download rights.** A catalogue result records missing main chapters, decimal
extras, duplicates/lock issues, possible series-title mismatches and listed language
tags. The site may not independently label the English translation. Successful
listing is **not** a test of image clarity, chapter contents, or source permissions.

## Running the audit

On the feature branch, pushing this workflow or the catalogue files automatically
starts **five separate metadata-only jobs**, up to two concurrently. Later it may
also be started with `workflow_dispatch`. Each uploads one small JSON report
with a seven-day retention. No source images, CBZs, passwords, browser profiles
or personal catalogue data are uploaded.

Local, after installing the pinned upstream CLI:

```powershell
python -m unittest tests.test_five_manga_catalogue -v
python scripts/five_manga_catalogue.py --slug love-hina --client manga-downloader --output reports/love-hina.json
```

Status meanings:

- `complete-numbered-metadata`: all expected positive chapter labels appear in
  the listing, with a matching series title, no locked entries, and no bad records.
  This **does not claim** that all pages exist, are English, or may be downloaded.
- `partial-or-uncertain-metadata`: some main chapters are absent, listed as locked,
  or contain malformed metadata; check the report before assessing feasibility.
- `review-title-mismatch`: the candidate page may refer to another edition/work.
- `unverified`: the site or CLI could not return an interpretable listing.

## Rights and further work

An unofficial reader's availability and the fact that a third-party tool technically
supports it do **not** establish permission to download, archive or publish the
copyrighted series. The current workflow therefore has **no chapter downloading
steps, no public CBZ artefacts and no Hugging Face uploads**. Do not bypass
logins, DRM, Cloudflare challenges or rate limits.

Before implementing any actual image retrieval, establish an authorised source and
its distribution terms. Prefer official publisher editions of
[Love Hina (Kodansha)](https://kodansha.us/series/love-hina-omnibus/),
[Love★Com (VIZ)](https://www.viz.com/love-com), and
[Nisekoi (VIZ)](https://www.viz.com/nisekoi-false-love).
Publisher e-books and subscription chapters are **not** assumed to support
DRM-free CBZ export.

See [the existing source feasibility assessment](REMAINING_MANGA_FEASIBILITY.md)
for MangaDex-hosted English gaps. For *Kainushi wa Akuma*, the 11 labels missing
from MangaDex remain a separate source-reconciliation task.
