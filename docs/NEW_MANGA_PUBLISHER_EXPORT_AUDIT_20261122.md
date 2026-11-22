# New-title publisher and DRM-free export audit

**Checked:** 22 November 2026  
**Scope:** the six new English manga targets only. Previously completed titles are excluded.

## Summary

No new current publisher/creator-authorised DRM-free English export was verified. **Love Hina remains the only identified portable-file route**, and it is a historical offer whose purchase entitlement is unknown. The other titles currently have no verified authorised DRM-free export route.

## Title-by-title status

| Priority | Title | Official English position | Portable export decision |
|---:|---|---|---|
| 1 | Kimi no Iru Machi | No current official English edition/export found. Historical Crunchyroll Manga licensing is not a current downloadable edition. MangaDex exact title has 0 English feed entries. | No authorised export identified. |
| 2 | Love Hina | Kodansha English Omnibus 1-5; current licensed reading listings also appear on MangaPlaza and GlobalComix. | Historical Humble Bundle DRM-free files are confirmed, but ownership is unknown. Current reader listings do not establish a downloadable file. |
| 3 | Lovely Complex / Love★Com | VIZ lists the complete 17-volume English edition, including digital volumes. The VIZ chapter reader currently reports regional unavailability. | No DRM-free CBZ/PDF/EPUB export verified. Kobo's English EPUB listing specifies Adobe DRM. |
| 4 | Mado kara Madoka-chan | Kodansha Japan lists the completed five-volume Japanese edition. No official English edition was found. | Japanese digital books are not English acquisition candidates. |
| 5 | Nisekoi: False Love | VIZ lists the complete 25-volume English edition and digital volumes. | No DRM-free CBZ/PDF/EPUB export verified. Kobo's English EPUB listing specifies Adobe DRM. |
| 6 | The Fairytale-like You Goes on the Assault | No authorised English edition/export found. English third-party translation records exist, but creator restrictions apply. | Do not treat community uploads as authorised files. Obtain explicit rights-holder permission before any acquisition. |

## Love Hina: the one historical DRM-free route

Kodansha and the Comic Book Legal Defense Fund announced the 2020 Kodansha Humble Manga Bundle on 20 May 2020. It included:

- Omnibus 1 at the $1 tier
- Omnibus 2 at the $8 tier
- Omnibus 3 at the $15 tier
- Omnibus 4 at the $18 tier
- Omnibus 5 at the $20 tier

The complete five-volume set therefore required the $20 tier. CBLDF explicitly described the files as DRM-free downloads. The promotion ended on 10 June 2020.

Sources:
- [Kodansha's 2020 bundle announcement](https://kodansha.us/2020/05/20/get-over-1500-worth-of-award-winning-manga-for-20-with-this-humble-manga-bundle-ends-69/)
- [CBLDF's bundle announcement and exact volume tiers](https://cbldf.org/2020/05/support-cbldf-get-award-winning-manga-from-kodansha-in-new-humble-bundle/)
- [CBLDF's final-week reminder and 10 June end date](https://cbldf.org/2020/06/last-week-to-support-cbldf-with-manga-humble-bundle/)

**Entitlement remains unverified.** No purchase receipt or owned CBZ/PDF/EPUB files were found in available project context. A Gmail search could not run because the connected action required interactive input in this non-interactive run. No previous conversation confirms the purchase. Do not assume ownership or attempt to access a Humble account.

## Current Love Hina reading listings are not verified exports

- [Kodansha Reader Portal support](https://kodansha.us/support-center/) says its digital content is accessed through the website and is not offered in downloadable formats.
- [MangaPlaza's Love Hina Omnibus listing](https://mangaplaza.com/title/0303000001/) presents a licensed English reading series. Its listing is not a portable CBZ/PDF/EPUB export.
- [GlobalComix lists Love Hina Omnibus 1-5](https://globalcomix.com/c/love-hina-omnibus/). Its [FAQ](https://globalcomix.com/support/faq) distinguishes DRM-free PDF sales from Collection Unlocks, which grant a licence to read. The public Love Hina release pages show generic Buy/Gold reading options, not an explicit PDF-download option. Treat them as reading access unless the release or publisher confirms a PDF sale.

## Publisher catalogue references

- [VIZ: Love★Com](https://www.viz.com/love-com) and [volume 17 digital listing](https://www.viz.com/manga-books/manga/lovecom-volume-17-0/product/2205).
- [VIZ: Nisekoi: False Love](https://www.viz.com/nisekoi-false-love) and [volume 25 digital listing](https://www.viz.com/manga-books/manga/nisekoi-false-love-volume-25-0/product/5379/digital).
- [Kodansha Japan: Mado kara Madoka-chan volume 1](https://www.kodansha.co.jp/comic/products/0000018936) and [volume 5](https://www.kodansha.co.jp/comic/products/0000315255).
- [Creator profile: Kazutake Hazano](https://twitter.com/teigi_3). The creator asks that the work not be reposted and translations not be published on overseas sites.

## Upstream downloader status

The latest upstream [Manga Downloader release](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0) is v25.3.0, published 18 November 2026. It supports 584 sites and adds chikari.moe, manhuaplus.top and manhuaplus.org, alongside repairs. These integrations do not establish that any target is present, that image retrieval works, or that export rights exist.

The existing [ManhuaTop four-title test](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44803983855) failed all four probes. Do not repeat those tests without a meaningful upstream change.

## Operational decision

- No new authorised source passed both rights and export checks.
- No media-download tests or resumable media batches were launched.
- No manga images or CBZs were retained.
- No public Actions or Hugging Face media distribution occurred.
- No secure private persistent runner/destination is configured.
- The owner's Windows machine is not accessible to this automation.

**Minimal next step for Love Hina:** check the Humble purchase history. If the $20 tier was purchased, download the five DRM-free CBZ volumes directly to the owner's Windows machine and run the existing local import/integrity checks. Otherwise, obtain a current publisher-authorised DRM-free export. The other five targets require a new authorised export or explicit rights-holder permission.
