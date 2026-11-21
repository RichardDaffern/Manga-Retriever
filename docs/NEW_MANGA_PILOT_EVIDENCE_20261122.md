# New manga pilot evidence ledger

**Audit date:** 22 November 2026  
**Scope:** Kimi no Iru Machi, Love Hina, Lovely Complex, Mado kara Madoka-chan, Nisekoi, and The Fairytale-like You Goes on the Assault only. Previously completed titles are excluded.

## Result

The five MangaKatana titles have **35 technically verified temporary CBZ archives containing 1,032 image pages** across two runs. Their reports contain 35 unique SHA-256 hashes. The media bytes were created in ephemeral public GitHub Actions workspaces and deleted after verification. The retained GitHub artefacts contain JSON receipts only, not CBZ files.

| Title | Sampled chapters | Temporary CBZs | Verified image pages | CBZ bytes reported |
| --- | --- | ---: | ---: | ---: |
| Kimi no Iru Machi | 1, 2-3, 130-131, 260-261 | 7 | 192 | 55,953,276 |
| Love Hina | 1, 2-3, 60-61, 119-120 | 7 | 216 | 62,640,600 |
| Lovely Complex | 1, 2-3, 33-34, 65-66 | 7 | 360 | 87,464,140 |
| Mado kara Madoka-chan | 1, 2-3, 37-38, 73-74 | 7 | 74 | 16,788,686 |
| Nisekoi | 1, 2-3, 114-115, 228-229 | 7 | 190 | 44,027,255 |
| **Total** |  | **35** | **1,032** | **266,873,957** |

These are spot checks, not full-series downloads. MangaKatana's chapter-list metadata previously reported 261, 120, 66, 74 and 229 numbered main chapters respectively. Only seven chapters per title were sampled. The other 254, 113, 59, 67 and 222 numbered chapters respectively remain **unverified**, not confirmed missing. Decimal extras and special chapters are also not fully audited.

## Mandatory language, rights and retention status

Every one of the 35 MangaKatana receipts reports:

- No explicit English label from the source.
- Manual English-page review required.
- Rights checked by the user but not independently verified.
- Public CI artefact publication not permitted.
- No Hugging Face upload.

No page text was visually reviewed in this automation run. The reports establish that image files could be decoded and counted, not that the pages are English, complete, authorised for archival retention or eligible for redistribution.

**Destination:** ephemeral GitHub Actions runner workspace only. No persistent private destination was recorded. CBZ files were deleted after the verification jobs. No CBZ bytes are retained by the repository, GitHub Actions artefacts or Hugging Face. The only retained outputs are the small JSON report artefacts listed below.

## Five first-chapter pilots

Run [44755633296](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44755633296). Each artefact is a JSON receipt only and expires on **23 November 2026 UTC**.

| Title | Artefact ID | Report size | Expires (UTC) | Temporary CBZ | Pages | CBZ bytes | SHA-256 |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Kimi no Iru Machi | 14638010391 | 648 B | 2026-11-23 14:41:22 | Kimi no Iru Machi 1 | 43 | 15,251,042 | 8fa37c938dda375c1582725be412ac156ee7b617693b879eec26102dcb907ef4 |
| Love Hina | 14636799475 | 636 B | 2026-11-23 14:41:58 | Love Hina 1 | 81 | 22,461,378 | 2944e4df6231b4d23d6e5e5b3f738bc9ffaa193133760bfb33cdb7b1b87fa5e7 |
| Lovely Complex | 14638046053 | 634 B | 2026-11-23 14:42:46 | Lovely Complex 1 | 53 | 11,507,205 | fdcceccb26918263882a666282fdbf0420e35af5a764c5fa21d138c83c056c31 |
| Mado kara Madoka-chan | 14639050165 | 668 B | 2026-11-23 14:42:19 | Mado kara Madoka-chan 1 | 14 | 2,291,499 | 74e2792c401b5eeeea3bcdf20d8105098b0d4dab0e96f53f31546cca277a27ba |
| Nisekoi | 14638515660 | 618 B | 2026-11-23 14:43:27 | Nisekoi 1 | 55 | 11,282,969 | 0751cf545b7f74a49cbeb0d9d81d9dd27fc6dd9e5557a2913fb88b46b2e6e48e |

## Fifteen early, middle and final chapter checks

Run [44783810968](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44783810968). The 15 artefacts below are JSON receipts only. All expire on **27 November 2026 UTC**. Together they report 30 temporary CBZ archives and 786 image pages.

| Title | Selected chapters | Artefact ID | Report size | Expires (UTC) | Temporary CBZ pages | CBZ bytes | SHA-256 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Kimi no Iru Machi | 2-3 | 14651384279 | 726 B | 2026-11-27 17:31:42 | 33 | 9,211,071 | 26e64e5ccdda9eaf6dd71955ac26cf0cf1e2391f1582f19a36ef0d657b88fcf6 |
| Kimi no Iru Machi | 2-3 | 14651384279 | 726 B | 2026-11-27 17:31:42 | 27 | 8,844,961 | ff2d180bcf16080953f24498c1f10a0ecf98f0568b75dbeeed8c9075d32d7664 |
| Kimi no Iru Machi | 130-131 | 14653336170 | 737 B | 2026-11-27 17:30:40 | 19 | 4,095,445 | 760e484675701e2b975a5fdea60e4e55ec94d549b003731f5eaf3e07455de430 |
| Kimi no Iru Machi | 130-131 | 14653336170 | 737 B | 2026-11-27 17:30:40 | 19 | 3,818,169 | 91d8091215cff69b8afdfd2361febfe5a1f40cdf18a7cd8ef51d0892786663e8 |
| Kimi no Iru Machi | 260-261 | 14653491084 | 747 B | 2026-11-27 17:31:39 | 21 | 5,563,491 | 08b5bc59171c02f5810a4d0fe7d9c9fe1966ade56ba3d7fd5ce28a30caf0fcd9 |
| Kimi no Iru Machi | 260-261 | 14653491084 | 747 B | 2026-11-27 17:31:39 | 30 | 9,169,097 | 61c95b7bca84f99f18cd1e7b7d73a999a9b5083244922bbb4fdc14cfcbf9e121 |
| Love Hina | 2-3 | 14653221916 | 736 B | 2026-11-27 17:32:18 | 25 | 7,274,971 | bf7f63053bc57161f7b06b6301ca8f14e7d816efa03dd860a541e255199f172d |
| Love Hina | 2-3 | 14653221916 | 736 B | 2026-11-27 17:32:18 | 19 | 5,599,546 | 2dba8c83eb461280c130635cbbee98dcbae1203e5fafc3ffa22aeff889adc9f8 |
| Love Hina | 60-61 | 14653381723 | 745 B | 2026-11-27 17:33:24 | 22 | 6,749,964 | ddbde5384ecec922be28a21d99eae48895d25a41b4660642a6c30a47028147ae |
| Love Hina | 60-61 | 14653381723 | 745 B | 2026-11-27 17:33:24 | 27 | 7,599,106 | 30ba50fe8aaa1001e9c49c986cacc1859df40f17e0ec29d32ab3c6ad1c833b4d |
| Love Hina | 119-120 | 14652709036 | 751 B | 2026-11-27 17:33:01 | 20 | 5,949,651 | a5429f22e83daf371f0c821c6a9463680af05d10f1bf12fb68e237bb0c368881 |
| Love Hina | 119-120 | 14652709036 | 751 B | 2026-11-27 17:33:01 | 22 | 7,005,984 | 8d62d6b7ca507c1af6e7a0f50f3e305a09e9f0150625ed074d4aebd89fd724a0 |
| Lovely Complex | 2-3 | 14651294597 | 714 B | 2026-11-27 17:34:35 | 47 | 9,774,223 | dd7d2a4575dffb6e413d83315abc5842b42b91f310884639103980f85137fdbc |
| Lovely Complex | 2-3 | 14651294597 | 714 B | 2026-11-27 17:34:35 | 45 | 9,933,770 | b4c68323cc483192950519c40e325bdd269f00198da330a9d85fd4c7d136e285 |
| Lovely Complex | 33-34 | 14654255723 | 719 B | 2026-11-27 17:35:09 | 49 | 10,273,210 | c3d67a6756a51a98f15b2ee21055f10e351e423ba198bd2a81cc778716cd3fff |
| Lovely Complex | 33-34 | 14654255723 | 719 B | 2026-11-27 17:35:09 | 49 | 11,831,541 | 79a31a416d052733698b7217e166350657b9ce7bcad44d773abb969a939df7ec |
| Lovely Complex | 65-66 | 14654231139 | 753 B | 2026-11-27 17:37:13 | 57 | 14,445,746 | b6054d609dcd42931f162973b3d1032a9b79641b90299579de5841849b3e5b61 |
| Lovely Complex | 65-66 | 14654231139 | 753 B | 2026-11-27 17:37:13 | 60 | 19,698,445 | 1511f2946a98db60ccb7cebc216d779bc3e26f1f61285ddadb2695b451f08380 |
| Mado kara Madoka-chan | 2-3 | 14654045872 | 751 B | 2026-11-27 17:35:06 | 10 | 2,016,904 | 7c3755642d93954480212f59725937bc66dd4d6f36dff2362ee13425ccd68601 |
| Mado kara Madoka-chan | 2-3 | 14654045872 | 751 B | 2026-11-27 17:35:06 | 10 | 2,014,884 | 1ff3cd25754f09302fe3fed7e35cee413237a6c30053531f0561dd2b69c55b0e |
| Mado kara Madoka-chan | 37-38 | 14653018945 | 766 B | 2026-11-27 17:36:07 | 10 | 2,289,464 | d481e09ce340149ff3f052bb9301835ff2354e6badc52a547ff87b26669f5e38 |
| Mado kara Madoka-chan | 37-38 | 14653018945 | 766 B | 2026-11-27 17:36:07 | 10 | 2,491,280 | 966767790c62853b65bc807b2d2104a268976881de52edb6e03c2bce9949f114 |
| Mado kara Madoka-chan | 73-74 | 14650959950 | 773 B | 2026-11-27 17:35:44 | 9 | 2,338,559 | 58d74d7c9a608644c37610c1369ec5087c296053246027407106d943915c12b6 |
| Mado kara Madoka-chan | 73-74 | 14650959950 | 773 B | 2026-11-27 17:35:44 | 11 | 3,346,096 | 5c7a7c04e504ab0ef266f9762cbfc52d435c80ba089564ffd4bb274636ae0762 |
| Nisekoi | 2-3 | 14653227821 | 700 B | 2026-11-27 17:37:17 | 26 | 5,824,981 | b3544067d43b2eb2160bbd75e1df5c76706a9653e605a0bad923ea70447e11ce |
| Nisekoi | 2-3 | 14653227821 | 700 B | 2026-11-27 17:37:17 | 24 | 5,832,527 | 0e09e003a193ff80f9b7f7ab757740b2bb73d7c0ddfc5fee4a6b6834dd6b8d0f |
| Nisekoi | 114-115 | 14654400804 | 707 B | 2026-11-27 17:37:00 | 20 | 4,943,373 | 5551926382081bd2fa6ce3655a7613c0cb0326ae4d0d64070f1a75223cbd5078 |
| Nisekoi | 114-115 | 14654400804 | 707 B | 2026-11-27 17:37:00 | 20 | 5,126,201 | 49d5277049fc854542ac4fa8b4c4cfd1eedcab007487d6f0929bd819708f8a13 |
| Nisekoi | 228-229 | 14652799592 | 723 B | 2026-11-27 17:38:00 | 20 | 5,179,718 | 650d4df38f0542b7de4db1b55ba0fdd4e228aae0c65c5dce7344419796a2b8a5 |
| Nisekoi | 228-229 | 14652799592 | 723 B | 2026-11-27 17:38:00 | 25 | 5,837,486 | de89ae3e4f024a29c27738ffc6e6e0238bc4147a8c4fc2266021dc6d06d8a91d |

## Fairytale pilot and creator restriction

Run [44789220759](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44789220759) retained only artefact **14655881240** (804 B), expiring **27 November 2026 18:04:13 UTC**. The report contains two JSON files:

- The listing summary records 72 chapter entries, 42 integer labels and 29 fractional labels. These counts do not reconcile to a unique 71-label inventory and require source-side reconciliation.
- The media receipt records one temporary Chapter 1 CBZ with 8 verified image pages, but user-owned file retention is false and no CBZ hash or persistent destination is present.

The creator's public profile explicitly prohibits reposting and asks that translations not be posted on overseas sites. The third-party English reader listing is not an authorised export. Do not retrieve or archive those English uploads without explicit written creator permission or a licensed edition.

## ManhuaTop failed diagnostics, not repeated

Run [44803983855](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44803983855) retained four diagnostic JSON artefacts only. All expired **27 November 2026 19:38 UTC**. No images were downloaded and archive rights were not verified.

| Title | Artefact ID | Size | Expires (UTC) | Error category |
| --- | ---: | ---: | --- |
| The Heavenly Demon Can't Live a Normal Life | 14659944929 | 559 B | 2026-11-27 19:38:43 | browser, Chromium, network |
| Disastrous Necromancer | 14660409466 | 519 B | 2026-11-27 19:38:38 | browser, Chromium, network |
| High-Martial World | 14661628427 | 566 B | 2026-11-27 19:38:28 | HTTP 403, browser, Chromium, network |
| Magic Emperor | 14662650937 | 490 B | 2026-11-27 19:38:31 | browser, Chromium, network |

Do not rerun these identical probes unless there is a meaningful upstream site/client change. Upstream Manga Downloader v25.3.0 (18 November 2026) remains the latest checked release, advertises 584 sites, and adds chikari.moe, manhuaplus.top and manhuaplus.org. Those additions do not establish an authorised source for these six titles.

## Publisher and rights leads

- **Love Hina:** Kodansha's 2020 Humble Bundle announcement included all five English Omnibus volumes in CBZ, PDF and ePub formats. The offer ended 10 June 2020. The owner's purchase entitlement and actual file DRM/terms remain unverified. The Gmail purchase-receipt search could not run in this non-interactive automation session because the connector required user input. The owner's account and Windows files were not accessed.
- **Love Hina, historical J-Comi:** the original Japanese 14-volume PDF distribution was author-authorised, but the operator's [official closure notice](https://closing.mangaz.com/) says the internet distribution service stopped on 26 November 2024. This is not a current source and is not the English edition.
- **Lovely Complex / Love★Com and Nisekoi:** VIZ provides official English digital reading and volume purchases, but no portable CBZ/PDF/EPUB export right was verified.
- **Kimi no Iru Machi:** historical English Crunchyroll Manga licence only; no current authorised English export was found.
- **Mado kara Madoka-chan:** Kodansha's completed five-volume edition is Japanese; no official English edition was found.
- **The Fairytale-like You Goes on the Assault:** the creator's reuse restriction rules out treating third-party English translations as an authorised acquisition source.

## Retailer file-format checks (22 November 2026)

Current official retailer listings reinforce the lack of a portable DRM-free English export:

| Target | Official English retailer evidence | Format / result |
| --- | --- | --- |
| Kimi no Iru Machi | Pika lists French digital volumes, including [volume 1](https://www.pika.fr/livre/town-where-you-live-t01-9782811624569/) and [volume 23](https://www.pika.fr/livre/town-where-you-live-t23-9782811628246/). Kobo's [volume 7 listing](https://www.kobo.com/ca/en/ebook/a-town-where-you-live-t07) identifies French language and Adobe DRM. | No English edition or export found. French EPUB3 is Adobe DRM. |
| Love Hina | Kobo's [English Omnibus 1 listing](https://www.kobo.com/ww/en/ebook/love-hina-omnibus-1-1) identifies Kodansha Comics, English language and EPUB3 with Adobe DRM. | Current retail EPUB is not DRM-free. The expired 2020 Kodansha Humble Bundle remains conditional on prior owner entitlement and inspection of the actual files. |
| Lovely Complex / Love★Com | Kobo's [English Love★Com Vol. 17 listing](https://www.kobo.com/us/en/ebook/love-com-vol-17) identifies VIZ Media and EPUB3 with Adobe DRM. | Official English edition exists, but the sampled retailer export is DRM-protected. |
| Mado kara Madoka-chan | Kodansha Japan's original five-volume edition remains Japanese. No English publisher or retailer edition was found. | No English export route. |
| Nisekoi | Kobo's [English Vol. 1 listing](https://www.kobo.com/in/en/ebook/nisekoi-false-love-vol-1) identifies VIZ Media and EPUB3 with Adobe DRM. | Official English edition exists, but the sampled retailer export is DRM-protected. |
| The Fairytale-like You Goes on the Assault | The creator's own public profile and terms restrict reposting and overseas translation uploads. | No creator-authorised English export. Do not use third-party English reader uploads. |

No DRM removal, account download, image extraction or source test was attempted. A DRM-protected retailer EPUB is not a DRM-free export and must not be bypassed. The official English VIZ editions remain usable for ordinary licensed reading, but no portable archive permission was established.

## Current repository and automation state

- PR [#43](https://github.com/RichardDaffern/Manga-Retriever/pull/43) corrected the Love Hina J-Comi status and was merged.
- PR CI [44946231900](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44946231900) passed.
- Post-merge main CI [44946312108](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44946312108) passed and produced no artefacts.
- Main commit after PR #43: 3cc2e705d5872e14a6a9963c8c04c685631adef7.
- No open PRs were present at the start of this evidence audit.
- Manga Storage Controller and Manga Library were not modified.

## Decision

No target has a verified route satisfying all four requirements: authorised export, English page text, complete chapter/volume coverage and a lawful persistent private destination. No new media batch was launched. No new title is claimed as downloaded or retained. The five MangaKatana pilots are technical evidence only; the Fairytale third-party English source is explicitly restricted by the creator.
