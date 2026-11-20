# Parallel English Manga Download Investigation

**20 November 2026.** Use the [six-track GitHub Actions investigation](../.github/workflows/parallel-remaining-manga-sources.yml) to evaluate the six unfinished manga **concurrently** instead of serially.

## Live parallel tracks

| Track | Title | Parallel checks | Actual pages downloaded |
| --- | --- | --- | --- |
| 1 | Kainushi wa Akuma | Pinned MangaDex English-feed pagination, integer/fractional labels and mismatch with a previously observed 56-entry alternative English listing | **None in this workflow** |
| 2 | Kimi no Iru Machi | MangaKatana exact chapter catalogue + independently pinned MangaDex publication metadata | **None in this workflow** |
| 3 | Love Hina | Same independent source checks, plus storefront DRM-free export research | **None in this workflow** |
| 4 | Lovely Complex | Same independent source checks; standard vs coloured MangaDex editions distinguished | **None in this workflow** |
| 5 | Mado kara Madoka-chan | Same independent source checks; English source/rights verification pending | **None in this workflow** |
| 6 | Nisekoi | Same independent source checks, plus storefront DRM-free export research | **None in this workflow** |

The five catalogue jobs use `strategy.max-parallel: 5`, `fail-fast: false`; Kainushi is a separate independent job running at the same time. All six outputs are titled `parallel-source-track-<slug>`. One title's failure does not cancel the others. No Japanese downloads, artwork bytes, DRM bypass, authenticated scraping or HF uploads occur.

These are **investigation jobs**, not manga chapter downloads. Metadata coverage and publication cover references **do not** constitute verified English chapter image downloads.

## New storefront evidence, verified independently

- **Love Hina, Neon Ichiban:** All five [Kodansha Love Hina Omnibus listings](https://neonichiban.com/item/3101/love-hina-omnibus-vol-1) are sold digitally, but their own detail views say the **publisher does not allow PDF downloads**. Search descriptions that label the product *DRM-free* are not proof it can be exported into Manga Library. Do not mark this a portable file source. Additional volumes: [2](https://neonichiban.com/item/3112/love-hina-omnibus-vol-2), [3](https://neonichiban.com/item/3113/love-hina-omnibus-vol-3), [4](https://neonichiban.com/item/3114/love-hina-omnibus-vol-4), [5](https://neonichiban.com/item/3116/love-hina-omnibus-vol-5).
- **Love Hina, Kobo:** The English digital omnibus is marked [Adobe DRM](https://www.kobo.com/ww/en/ebook/love-hina-omnibus-1-1), so the current non-DRM EPUB importer cannot use it.
- **Nisekoi, Kobo:** English [EPUB3 is marked Adobe DRM](https://www.kobo.com/us/en/ebook/nisekoi-false-love-vol-1). The [official VIZ English edition](https://www.viz.com/nisekoi-false-love) supports online/app reading, not a confirmed local CBZ export.
- **Kainushi wa Akuma:** [OniSaga lists 56 English entries](https://onisaga.com/manga/kainushi-wa-akuma), but distinct labels are not necessarily equivalent to MangaDex's feed entries and have not been independently verified as authorised portable files.
- **Kimi no Iru Machi, Lovely Complex, Mado kara Madoka-chan:** Unofficial online chapter lists exist, but the existing source research has **not** established a permitted standalone English download.
  
## Workflow agreement for future work

1. Open concurrent, independent source research tracks for **all** unfinished titles. Each must record a stable manga identifier, the English edition, expected chapters/extras, image access, actual file checks and rights/export status.
2. Run authorised image/EPUB/PDF proof-of-concept downloads **per title** when a legally usable source is confirmed; verify original bytes, language and chapter coverage.
3. Group successful independent chapter batches in GitHub Actions, retry failures without blocking other titles, and publish actual image-containing media artefacts separately from discovery metadata.
4. Never claim success when only a catalogue, source identifier or cover reference was retrieved. Preserve a status distinction: `listed`, `English source verified`, `authorised to export`, `image bytes verified`, `CBZ/EPUB packaged`, `HF uploaded`, `visible in Library`.

Do not wait for every title to finish research before proceeding with a **different** title that has a suitable, permitted English source.
