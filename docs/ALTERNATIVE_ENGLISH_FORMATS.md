# English image, ZIP, CBZ and EPUB routes: live GitHub Actions proof

**20 November 2026.** This route preserves original English image bytes. All media is downloaded by **GitHub Actions**, not the user's computer.

## Confirmed real download

[Successful workflow run 44686201935](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44686201935) fetched the **six full-resolution English images** of creator-licensed *Pepper&Carrot* Episode 26 directly from the official high-resolution page, validated the Controller v1 export, and published a **seven-day GitHub Actions artefact** containing:

| File | Content | Integrity |
| --- | --- | --- |
| `english-original-images.zip` | Six original English JPEG images under `pages/`, attribution and SHA-256 manifest | Every original image SHA-256 verified |
| `english-fixed-layout.epub` | EPUB 3 image-page edition, English metadata and attribution | Image bytes rechecked against original SHA-256, EPUB mimetype first/uncompressed |
| `English-PepperCarrot-Episode26.cbz` | Existing independently verified chapter CBZ | Same original six pages; the Controller export was verified |
| `verification.json` | Source, licence, page count, filename, size and archive SHA-256 | Generated after validation |
| `ATTRIBUTION.txt` | David Revoy, contributors/credits URL and CC BY 4.0 | Required reuse attribution |

This confirms an **actual image/media download**, not a successful chapter-list query. The artefact expires **27 November 2026**. The workflow run page's Artefacts section contains the download.

Source and licence: [Official episode 26](https://www.peppercarrot.com/en/webcomic-sources/ep26_Books-Are-Great.html) and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This is an **English webcomic used as a source-licensed integration test**, not one of the five requested Japanese manga series. It should not be represented as their downloaded files.

## Engineering

- Exact fixed source, no arbitrary URL or publisher scraping.
- Check original English source-language tag, exact six-source-page manifest, CC BY licence, attribution, all decoded JPEG images, page SHA-256 and complete Controller export.
- Package ZIP and fixed-layout EPUB with original JPEG bytes unmodified. Independently open and validate the generated archives.
- Synthetic offline regression tests cover actual byte equality, XML structure, corruption, English-only guard, attribution and overwrite protection.
- [Workflow](../.github/workflows/english-alternative-formats.yml) can be manually dispatched after merge.
- No private user credentials, paid API, DRM removal, paywall bypass or Hugging Face upload.

### Local format packaging (for the fixed verified source)

```powershell
py -3.12 -m manga_retriever peppercarrot --episode 26 --output downloaded\english-26 --registry .manga-retriever\ids.json
py -3.12 -m manga_retriever verify --export downloaded\english-26
py -3.12 -m manga_retriever.alternative_formats --export downloaded\english-26 --output deliverables\english-26
```

## Remaining five English titles

| Manga | Known chapter index | Actual GitHub Actions artwork status |
| --- | --- | --- |
| Kimi no Iru Machi | 261 main + 16 extras | **Not downloaded** |
| Love Hina | 120 main + 3 extras | **Not downloaded** |
| Lovely Complex | 66 main + 2 extras | **Not downloaded** |
| Mado kara Madoka-chan | 74 main + 2 extras | **Not downloaded** |
| Nisekoi | 229 main + 11 fractional extras + Ch. 0 | **Not downloaded** |

The [catalogue audit](FIVE_MANGA_CATALOGUE.md) did not verify English artwork, permitted exports or redistribution rights. **The existence of these listings alone does not authorise full-series downloads or publishing copyrighted files in public GitHub Actions.** Do not enable the new workflow for them without source-specific authorisation.

Next engineering options: ingest DRM-free English EPUBs and image ZIPs purchased or received with appropriate rights, verify original bytes, and import them into the Manga Storage Controller. Official publishers can separately provide app-based offline reading that does not yield transferable files.

## Official English digital source research

- [Omoi's FAQ](https://www.omoi.com/faq) says some individually selected series support DRM-free EPUB downloads and requires checking each series' Volumes tab; this is **not** confirmation that *Love Hina* offers EPUB.
- [GlobalComix](https://globalcomix.com/news/details/339/1) permits PDF purchases/downloads for selected releases. An official [Love Hina Omnibus catalogue](https://globalcomix.com/c/love-hina-omnibus/) exists, but **a downloadable PDF for these exact omnibuses remains unconfirmed**.
- [Kodansha English Love Hina](https://kodansha.us/series/love-hina-omnibus/) offers digital volumes, but the Kodansha Reader Portal is not itself a portable-file downloader.
- [VIZ Love★Com](https://www.viz.com/vizmanga/chapters/love-com) and [VIZ Nisekoi](https://www.viz.com/shonenjump/chapters/nisekoi) provide official English digital reading. Their app offline files are not established as exportable EPUBs or image ZIPs.
