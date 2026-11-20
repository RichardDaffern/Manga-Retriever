# English DRM-free EPUB import into Manga Controller

**Implemented, live-tested on 20 November 2026.** This route supports a DRM-free English manga EPUB you have permission to retain. It makes one verified, volume-labelled manga chapter per EPUB file, preserving embedded original image bytes, and writes the Controller v1 candidate plus CBZ archives.

## Live GitHub Actions verification

The [English EPUB Download to Manga Controller Pilot](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44693718612) actually downloaded creator-licensed English high-resolution pages from Pepper&Carrot Episode 26, assembled an EPUB, reimported that EPUB through this new code, verified each original image SHA-256 and uploaded a **real EPUB/CBZ/Controller export artefact**.

- Six verified English image pages, one chapter, one Controller candidate.
- ZIP/EPUB and subsequent CBZ both preserve the image bytes.
- The example is a permitted source-licensed *technical pilot*, **not** one of the five outstanding commercial manga downloads.
- The generated artefact expires **27 November 2026**.

## Windows usage

Single DRM-free, image-based English EPUB:

```powershell
py -3.12 -m manga_retriever.epub_import --source "C:\Manga\my-book.epub" --output "C:\Manga\verified-epub" --registry "C:\Manga\registry.json" --series-title "My Manga" --acknowledge-rights
py -3.12 -m manga_retriever verify --export "C:\Manga\verified-epub"
```

Multiple complete English manga volumes (directory must contain only EPUB files):

```powershell
py -3.12 -m manga_retriever.epub_import --source "C:\Manga\My Series EPUBs" --output "C:\Manga\verified-series" --registry "C:\Manga\registry.json" --series-title "My Series" --acknowledge-rights
```

Do not reuse an output folder. Back up the stable ID registry. To use GitHub Actions on private purchased files, a permitted and appropriately secured file-transfer mechanism would need separate implementation; the existing test workflow downloads **only creator-licensed media**.

## Supported and excluded EPUBs

- **Supported:** EPUB 3 fixed-layout manga with English OPF `dc:language` metadata; each reading-order XHTML page includes exactly one JPG, PNG, WebP or supported AVIF image. Images are extracted in their EPUB spine order, preserved byte-for-byte and validated by the Controller importer.
- **Supported:** multiple EPUB volumes grouped under one series using `--series-title`. Each volume becomes a chapter-labelled entry; the importer does **not** infer original serial chapter boundaries inside a whole omnibus.
- **Rejected:** Japanese or mixed/unknown languages, `META-INF/encryption.xml`, ACSM/Adobe DRM/Kindle DRM, remote images, unsupported CSS-only or canvas-based pages, XML entities/DTDs, malformed archives, unsafe paths, symlinks, duplicate page images, excessively compressed archives and unexpected extra page elements.
- **Out of scope:** DRM removal, scraping authenticated readers, converting publisher-protected digital books, arbitrary web URLs, automatic paid purchases, and uploading copyrighted books to public GitHub Actions.

## Specific requested manga: evidence as of 20 November 2026

| Title | Official English electronic edition | Portable English file availability |
| --- | --- | --- |
| Love Hina | [Omoi](https://www.omoi.com/series/love-hina), [Kodansha](https://kodansha.us/series/love-hina-omnibus/), [Kobo](https://www.kobo.com/ww/en/ebook/love-hina-omnibus-1-1) | Omoi listing does not display its advertised **DRM-free EPUB badge** for the five volumes; Kobo's English EPUB is marked **Adobe DRM**. No permitted unrestricted file was demonstrated |
| Nisekoi | [VIZ](https://www.viz.com/shonenjump/chapters/nisekoi), [Kobo India](https://www.kobo.com/in/en/ebook/nisekoi-false-love-vol-1) | Kobo lists 25 English EPUB volumes but explicitly marks EPUB3 **Adobe DRM**. VIZ app-based offline access does not supply an external DRM-free EPUB |
| Lovely Complex | [VIZ Love★Com](https://www.viz.com/love-com) | No verified DRM-free portable edition |
| Kimi no Iru Machi | Earlier English Crunchyroll Manga translations; no currently verified official English digital publisher | No verified DRM-free portable edition |
| Mado kara Madoka-chan | Japanese Kodansha publication; no verified complete official English edition | No verified DRM-free portable edition |

**Additional storefront route:** From 20 January 2026, Amazon can expose an EPUB/PDF download for **publisher-enabled DRM-free titles**. That availability is per book, not a universal Kindle feature. No requested title has been verified as qualifying. [Amazon's official documentation](https://kdp.amazon.com/en_US/help/topic/GDDXGH9VR22ACM8U?pubDate=20251212).

**No chapters of the five requested manga were downloaded** during this work. Technical compatibility of a format is not copyright/export authorisation for a specific title. Full image/page content must be available under the applicable permissions before creating or sharing GitHub Actions artefacts.
