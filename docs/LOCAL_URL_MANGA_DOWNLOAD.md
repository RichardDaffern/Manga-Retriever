# Actual URL-based manga chapter downloads: five-title pilot

**20 November 2026.** The site [MangaKatana](https://mangakatana.com/) displays a **Read offline** link on each of these five series pages, and the third-party [Manga Downloader v25.3.0](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0) implements their chapter URL format.

This feature is a **local-only, owner-run downloader** with independent CBZ image verification. It does NOT transfer copyrighted manga pages to public GitHub Actions artefacts or Hugging Face. Neither an online listing nor a downloader supporting the site establishes the copyright owner's permission to copy or redistribute a work; check source terms and your local use rights first.

## Windows usage

Install [the Windows CLI release](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0) and put `manga-downloader.exe` on your PATH. Do not install it into Windows System32. Install Manga Retriever's Python requirements using:

```powershell
py -3.12 -m pip install -e .
```

Download a **real chapter 1** and verify its image bytes, for example:

```powershell
py -3.12 -m scripts.local_url_manga_download --url "https://mangakatana.com/manga/nisekoi.553" --chapters 1 --output "C:\Manga\Nisekoi\Pilot-1" --acknowledge-local-rights
```

For an authorised second batch after inspecting the English pages:

```powershell
py -3.12 -m scripts.local_url_manga_download --url "https://mangakatana.com/manga/nisekoi.553" --chapters 2-20 --output "C:\Manga\Nisekoi\Batch-2-20" --acknowledge-local-rights
```

Each batch is **at most 20 numbered chapters**, in a new output folder. The script refuses to overwrite folders, download all hundreds at once, or add hidden site credentials, DRM bypass or challenge-solving. It preserves JPEG/PNG/WebP/AVIF original bytes where possible, validates real pages in each CBZ, checks archive hashes, and publishes a `download-report.json` alongside downloaded CBZs only after the entire selected batch passes validation.

The other four reviewed URLs:
- `https://mangakatana.com/manga/kimi-no-iru-machi.2162`
- `https://mangakatana.com/manga/love-hina.4545`
- `https://mangakatana.com/manga/lovely-complex.6103`
- `https://mangakatana.com/manga/mado-kara-madoka-chan.21642`

## Run five series in parallel and retain your files on Windows

Create your private output folder first, outside the repository, for example `C:\\Manga\\Downloads`. From the cloned Manga Retriever directory, after installing the [pinned downloader CLI](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0), launch **all five first chapters simultaneously across two source workers**:

```powershell
py -3.12 -m scripts.local_url_manga_bulk --mode pilot --slugs all --workers 2 --output-root "C:\Manga\Downloads" --acknowledge-local-rights
```

The five real, verified chapter CBZs remain in private local subfolders. Inspect their page text to confirm English. **Only after reviewing the actual English pages** and source download terms, run all numbered chapters in **resumable 20-chapter batches**, across two independent series:

```powershell
py -3.12 -m scripts.local_url_manga_bulk --mode full --slugs all --workers 2 --output-root "C:\Manga\Downloads" --acknowledge-local-rights --confirm-english-reviewed
```

Progress is recorded as `manga-bulk-status.json`. On retry, previously verified folders are checked and skipped; incomplete/failed titles do **not** block the other titles. Existing files are never overwritten. This may consume substantial disk space and take considerable time. Expected main chapter counts from the metadata catalogues are 261, 120, 66, 74 and 229 respectively, but those figures do not establish that every chapter's actual image files are reachable.

No GitHub Actions workflow saves these full copyrighted chapters. This local-only command is the way to **retain** them privately, subject to applicable permissions.

## Confirmed live image-download pilots, 20 November 2026

[Five real one-chapter image checks](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44755633296) **all passed**. These tests downloaded real source images in the ephemeral runner, produced five valid CBZ archives and verified original image content. Counts:

| Title | Chapter | Real verified image pages |
| --- | --- | ---: |
| Kimi no Iru Machi | 1 | 43 |
| Love Hina | 1 | 81 |
| Lovely Complex | 1 | 53 |
| Mado kara Madoka-chan | 1 | 14 |
| Nisekoi | 1 | 55 |
| **Total** | **5 chapters** | **246** |

All five were marked `verified-image-files-needs-english-review`, because MangaKatana does not mark these chapters with an explicit English language field. The **technical** download path works, but this does **not** prove that every chapter is English, that all numbered/extras can be downloaded, that the source's images match publisher originals, or that the user has the copyright owner's permission to archive them.

**None of the five CBZ archives was published or retained in the public GitHub Actions artefacts.** The image files were removed from the runners after verification. For files you can keep privately on Windows, use the CLI above after checking the relevant permissions.

## English-only requirement and publication status

MangaKatana's chapter metadata may **lack an explicit language field**. In that case the report says `requiresManualEnglishReview: true` and labels the downloaded files `verified-image-files-needs-english-review`. This is a quarantine result, **not** a claim that the actual page text is English. Do not import Japanese/unknown-language pages into the English-only Manga Library. Inspect the real pages before marking them verified.

## Parallel technical checks (GitHub Actions)

[Five Real English Manga Chapter Download Pilots](../.github/workflows/five-real-chapter-download-pilots.yml) starts five independently isolated one-chapter probes, two concurrently to reduce source load. Each actually attempts downloading chapter 1 through the site's supported downloader and runs a CBZ image integrity test.

**Important:** Public CI deletes the downloaded files on the runner and publishes **only JSON verification results**, not the chapter pages/CBZs. A successful CI pilot proves technical image downloadability, **not persistent user-owned media, source copyright rights or confirmed English page content**. To retain source-authorised files, run the local Windows command above.

The workflow fails visibly for unavailable images, missing pages, invalid CBZs, unexpected responses or challenge/credential requirements. Failed attempts produce no media artefacts. No private HF or Controller changes occur.

## Handover to Manga Storage Controller

After validating the English page text and permission, the owner may import locally retained CBZs using:

```powershell
py -3.12 -m manga_retriever import --source "C:\Manga\Nisekoi\Batch-2-20" --output "C:\Manga\Nisekoi\Controller-Export" --registry "C:\Manga\private-ids.json"
py -3.12 -m manga_retriever verify --export "C:\Manga\Nisekoi\Controller-Export"
```

This exports a **draft Controller candidate**, not a direct upload or a backfill. Keep the ID registry private and backed up. Review and reconcile existing manga IDs through the Storage Controller before private uploads. Never identify a downloaded numbered batch as a completed manga unless full expected chapter coverage is verified.
