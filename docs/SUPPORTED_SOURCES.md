# Supported sources

**Implemented:** local folders, ZIP and CBZ archives supplied by the owner. Supported image formats PNG/JPEG/WebP and AVIF if Pillow supports the codec. This does not confirm ownership or licence.

**Proposed / not implemented:** Pepper&Carrot licensed web acquisition, MangaDex metadata-only research, selected NDL public-domain media and individually licensed creator archives. See [source research](SOURCE_RESEARCH.md). No arbitrary website or API URL can be downloaded using this version.

## Implemented licensed webcomic pilot

Pepper&Carrot Episode 26 (English high-resolution 6 pages) uses a fixed official source-page/URL allowlist and CC BY 4.0 licence check. All other episodes and websites remain unimplemented. The resulting package records exact URL/hash per page in `download_manifest.json` and preserves required attribution. No unofficial manga source has download support.

## Local creator-authorised PDF manga

The creator-published [*Give My Regards to Black Jack*](https://densho810.com/free/) PDF volumes can now be imported offline using `python -m manga_retriever.blackjack_pdf` after you download originals manually and explicitly declare `--official-source`. The converter produces rasterised PNG pages, CBZs and a Controller candidate. **It does not independently authenticate the PDFs, fetch them from the website or authorise publishing them to e-book stores or public GitHub Actions.** Attribution and the original owner's terms apply. [Guide](BLACKJACK_PDF_IMPORT.md).
