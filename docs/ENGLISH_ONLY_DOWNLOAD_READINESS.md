# English-only remaining manga: actual download readiness

Research date: **20 November 2026**. Owner directive: **English only**, original page quality wherever available. Japanese originals and fan-created translations of Japanese files are not substitutes.

## Important distinction

All five MangaKatana series returned the expected **chapter numbers** in [the live catalogue audit](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44679559853), but that audit used `list --json`. **It did not download image bytes, verify the language or publish CBZs.** The earlier assessment of technical chapter availability cannot be represented as an actual download. Every one of the five remains **not download-ready** under the repository's source-authorisation requirements.

## English source choices and blockers

| Title | Confirmed official English source | Download readiness for portable local manga files |
| --- | --- | --- |
| **Kimi no Iru Machi** | None established. [Weeb Central lists its edition as *Official Translation: No*](https://weebcentral.com/series/01J76XY7F049Y3WQ1WM57D8VGD/Kimi-No-Iru-Machi). | No authorised English standalone CBZ/PDF/EPUB source verified. |
| **Love Hina** | [Kodansha English Omnibus](https://kodansha.us/series/love-hina-omnibus/), five complete digital omnibuses. [Kodansha's GlobalComix listing](https://globalcomix.com/c/love-hina-omnibus/) also supplies English reading. | [Kodansha support](https://kodansha.us/support-center/) says its Reader Portal content is not offered in downloadable formats; a portable PDF/CBZ option for these specific editions has not been verified. |
| **Lovely Complex / Love★Com** | [VIZ official Love★Com](https://www.viz.com/love-com), 17 volumes. | The [VIZ Manga digital subscription](https://www.viz.com/company-faq) is unavailable in India according to VIZ's supported-region list; no standalone downloadable CBZ confirmed. |
| **Mado kara Madoka-chan** | No official English edition established; Japanese Kodansha publication exists. | No authorised English standalone download verified. |
| **Nisekoi** | [VIZ Shonen Jump English chapters](https://www.viz.com/shonenjump/chapters/nisekoi), with Shonen Jump membership in India. | Shonen Jump supports app-based offline downloads, not a verified external CBZ/PDF export. |
| **Kainushi wa Akuma** | No complete official English edition established. 45 labels were previously available on MangaDex, with 11 additional labels listed by OniSaga. | Remaining 11 labels are not verified as downloadable English CBZs with permission; the previous batch is partial. |

## What can be done without breaking the requirements

1. Use **official app-based offline reading** for *Nisekoi*, or publisher/retailer digital reading for *Love Hina* and, where geographically accessible, *Love★Com*. App offline storage is not a portable format for this library.
2. Import files for which the owner has a legitimate, **non-DRM, permitted** local copy, using the existing Windows Manga Retriever importer. The importer verifies images and archives locally and produces CBZ/controller candidate packages without GitHub hosting.
3. For any future automated English series: confirm the exact English edition, verify permission to archive/export, then test one chapter's actual pages and quality. Only after those checks may download jobs be enabled.
4. **Do not trigger a new public media-download workflow** solely on the basis of MangaKatana or Weeb Central catalogue counts. Public GitHub Actions artefacts can expose copyright-protected artwork.

Source licensing, downloadable versus app-only formats, actual English artwork and chapter completeness are independent checks. Do not treat successful metadata CI as evidence that any of those checks passed.
