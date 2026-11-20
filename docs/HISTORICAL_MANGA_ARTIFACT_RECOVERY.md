# Recover existing manga chapter downloads before they expire

**Verified against GitHub Actions on 20 November 2026.** This is a recovery guide for *existing* uploaded artifacts, not permission to distribute copyrighted manga or an assertion that every series is complete.

**Priority:** Most of the existing artifact files expire on **26 November 2026**, with Onizuka expiring **27 November 2026**. Download privately to your Windows machine before they expire.

## Existing live artifact inventory

| Title | Chapter jobs recorded | GitHub Actions | Pinned artifact count |
| --- | --- | --- | ---: |
| **ReLIFE** | 1-222 | [12 successful jobs](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44547390262) | 12 |
| **Love So Life** | 1-106 plus five decimal extras | [6 main jobs](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44597036262), [extras job](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44598620970) | 7 |
| **Last Game** | 1-56 | [3 successful jobs](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44587087000) | 3 |
| **Kaichou wa Maid-sama!** | 1-85 | [5 successful jobs](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44587087000) | 5 |
| **Onizuka-chan and Sawarida-kun** | 1-49 | [3 successful recovery jobs](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44675324997) | 3 |
| **Kainushi wa Akuma** | 3 partial listed batches | [partial successful jobs](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44597755913) | 3 |

The mixed-title workflow containing Last Game and Maid-sama! concluded **failure overall**, because its Onizuka jobs failed, but its eight individual Last Game/Maid-sama! jobs **succeeded and uploaded actual media artifacts**. A separate Onizuka retry subsequently succeeded.

All **33 selected exact artifact IDs** and the particular latest Kainushi batch 3 ID are pinned in [the recovery manifest](../scripts/historical_manga_artifacts_20261120.json). The public downloaded_manga.json registry being empty is **not** evidence these historical artifacts do not exist.

**Evidence:** A real [Onizuka chapters 41-49 ZIP](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44675324997) was inspected; it included 13 chapter CBZ files, and the producer's quality report recorded 9 main chapters, three fractional extras, Chapter 0 and 47 image pages. Inspecting a producer report is useful but does not replace independent image and hash verification.

## Windows, one command for six series

Install [GitHub CLI](https://cli.github.com/) and Python 3.12. In your Manga Retriever checkout, run:

    gh auth login
    gh auth status
    py -3.12 -m pip install -e .

Then retrieve all six series and their 33 existing artifacts, with three concurrent workers:

    Recover-Existing-Manga.cmd "C:\Manga\Recovered" all 3

Or retrieve two sets first:

    Recover-Existing-Manga.cmd "C:\Manga\Recovered" last-game,onizuka-sawarida 3

Equivalent Python command:

    py -3.12 -m scripts.recover_existing_manga --titles all --output-root "C:\Manga\Recovered" --workers 3

**What it does:** Reads the exact artifact identity from the manifest; checks GitHub metadata, run ID, name, expiration and reported file size; downloads each real artifact ZIP via authenticated GitHub CLI; validates safe archive paths and ZIP contents; opens every CBZ and decodes its actual image pages, dimensions and SHA-256; cross-checks any included producer image-count audit; then atomically publishes the verified chapter files in a private local folder.

**Retries:** Existing outputs are verified before skipping, never silently overwritten. A corrupt folder raises an error so you can inspect/move it first. Each title and chapter range proceeds independently. The command writes a private historical-recovery-status.json with per-artifact successes/failures and image counts, plus recovery-verification.json within each recovered artifact folder.

**Space:** The 33 existing artifact files total several gigabytes. Keep extra space for decompression and temporary ZIPs. Do not put the recovery folder inside the public repository. The command **never** uploads media back to GitHub or Hugging Face, touches the Reader, or edits your existing private manga catalogue.

**Limits:** GitHub reports the artifacts unexpired as of 20 November. Seven-day artifacts can expire or be deleted; a historical registry is not a permanent store. A successful job plus a verified CBZ does not automatically establish independent publisher-original image quality, English page text or complete source-translation coverage.

## Fifteen additional actual chapter-image tests

The [15-job GitHub Actions workflow](../.github/workflows/fifteen-manga-image-coverage-checks.yml) launches parallel real chapter download verification for **Kimi no Iru Machi, Love Hina, Lovely Complex, Mado kara Madoka-chan and Nisekoi**. Each title has two early, two middle and two late chapter files requested from its approved MangaKatana URL, across 15 jobs with three concurrent workers.

These are **real image downloads** on temporary runners and produce per-chapter ZIP/CBZ image verification reports. **Public CI deletes third-party artwork and uploads JSON-only technical receipts.** It cannot provide retained manga downloads; successful tests prove technical reachability, not source licence, English page text, full-series completeness or local storage.

For private, owner-authorised local retention of those five series after checking actual English pages and source permissions, use the already implemented [Windows URL bulk downloader](LOCAL_URL_MANGA_DOWNLOAD.md):

    py -3.12 -m scripts.local_url_manga_bulk --mode full --slugs all --workers 2 --output-root "C:\Manga\NewSeries" --acknowledge-local-rights --confirm-english-reviewed

This downloads in bounded 20-chapter batches, resumes verified batches and records per-title failures. Confirm exact rights, language and chapter coverage before importing a resulting candidate into the Manga Storage Controller.

## Live 15-job technical verification result (20 November 2026)

[**All 15 actual image-download jobs passed**](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44783810968). Each job downloaded and opened **two image-containing chapter CBZ files**: 30 independently verified CBZ archives, **786 decoded image pages** across five requested titles and three chapter positions each.

| Title | Beginning | Middle | End | Verified page total |
| --- | --- | --- | --- | ---: |
| Kimi no Iru Machi | 2-3 (60 pages) | 130-131 (38) | 260-261 (51) | 149 |
| Love Hina | 2-3 (44) | 60-61 (49) | 119-120 (42) | 135 |
| Lovely Complex | 2-3 (92) | 33-34 (98) | 65-66 (117) | 307 |
| Mado kara Madoka-chan | 2-3 (20) | 37-38 (20) | 73-74 (20) | 60 |
| Nisekoi | 2-3 (50) | 114-115 (40) | 228-229 (45) | 135 |
| **Total** | | | | **786** |

All 15 receipts were marked `englishReviewRequired=true` because the source listing did not label the downloaded page text. **The 30 CBZ image files were deleted from public runners**, not retained for the owner's download. The successful last-chapter probes do not prove that every intervening chapter or complete English publication exists. The local Windows bulk downloader remains the owner-retention path where permitted.

## Real recovery tool integration test

[**Licensed real GitHub artefact recovery test**](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44785614388) succeeded: the new recovery command fetched an *existing* creator-licensed Pepper&Carrot GitHub artefact using its exact unique GitHub artefact ID, extracted it safely and independently decoded **1 real CBZ archive containing 6 actual image pages**. The runner deleted the media after verifying it and published no copies. This validates the download-and-verify mechanism using legal sample media; the six commercial series still require private local retrieval by the owner to verify their complete sets.

## Copyright, access and identity safeguards

This local recovery helper only retrieves files already published by the existing GitHub Actions runs. It does **not** authorise or perform new republication of copyrighted chapter files. Original media, user permissions and personal IDs remain outside Git. No DRM/paywall/anti-bot bypass is supported. Korean or unverified-language files must not be silently imported into the English Manga Library. A title's full main-chapter-job range requires actual file coverage verification before being called complete.
