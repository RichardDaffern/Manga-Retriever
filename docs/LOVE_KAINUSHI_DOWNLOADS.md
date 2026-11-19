# Additional English MangaDex downloads, 20 November 2026

## Requested source targets and automated batches

- **Love So Life** by Kaede Kouchi: 106 numbered English main chapters, 5 English decimal-numbered extras, 119 feed entries containing duplicate releases. [Six bounded GitHub Actions batches](../.github/workflows/love-so-life-download.yml) target main chapter ranges 1–20, 21–40, 41–60, 61–80, 81–100 and 101–106. Each job requests uploader-original images, checks every page/CBZ, and verifies that every numbered main chapter in its target range exists. **Decimal extras are not guaranteed by these six main-chapter batches**; the independent metadata source lists 33.5, 33.6, 63.5, 75.5 and 99.5.
- **Kainushi wa Akuma** by Eiri Kaji: 45 distinct English chapter labels on MangaDex, including many decimal fractions and missing integer chapters. The [three independent GitHub Actions batches](../.github/workflows/kainushi-available-download.yml) partition current labels as 1 up to (not including) 10, 10 up to 19, and 19 up to 26, and inspect each CBZ by its **exact fractional chapter label**. Failed jobs retain any verified partial results and identify missing chapter labels in the audit. **No workflow marks this as a full series**.
- [Kainushi's independent English chapter index](https://onisaga.com/manga/kainushi-wa-akuma) lists 56 labels, with 11 labels absent on MangaDex: 1.1, 3, 4, 5, 6, 7, 8, 9, 9.5, 16 and 18. A complete archive cannot be claimed from MangaDex alone.

All downloads are source-title allowlisted, English-only and rate-limited, using pinned mangadex-downloader==3.1.4 and CBZ page hash/decode verification. Files are available via GitHub Actions **seven-day artefacts** and never committed into git or copied to Hugging Face. The public repository's artefacts can also be accessible to other readers. Before sharing, review MangaDex's API terms and each original creator/scanlator's rights. Access to online chapters does not establish a licence for redistributing copyright artwork.

GitHub Actions may fail on missing, external-only, rate-limited or already-removed scans; a passed workflow is evidence only for the requested main-numbered chapters/recorded labels and the integrity of archived files, not independent publisher-master resolution or completeness of all extras.

## Existing downloads

The ReLIFE run completed 12/12 batch jobs. The previous three manga (Maid-sama!, Last Game, Onizuka-chan) run independently of these new two-title workflows and its existing bounded recovery remains enabled.
