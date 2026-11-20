# Highest priority: Acquainted: Encounter Spin-Off (user-selected MangaDex ID)

**Date:** 20 November 2026
**Priority:** P0, ahead of other pending manga
**User-supplied URL:** https://mangadex.org/title/90f7c7a6-b759-4afb-b1cb-1af4660df307
**Verified MangaDex source title:** Acquainted: Encounter Spin-Off
**Live CI:** https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44758238680

## Exact-title findings

The exact-ID MangaDex audit, not a fuzzy web title match, confirms:

- English MangaDex feed entries: **0**
- MangaDex English numbered chapters: **0**
- MangaDex original English image paths: **none to sample**
- Verified original English image downloads or CBZ: **0**
- No cloud storage or private HF writes performed

**This MangaDex URL is not an English chapter download source at present.**
Do not trigger an empty CBZ job, silently download Korean, label metadata a download, or substitute a different title/edition.

## Korean and every-language MangaDex availability (20 November 2026)

A separate [live Korean availability audit](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44761569133) queried the **exact owner-selected title UUID**, filtered for `ko` and then for **all languages combined**, explicitly including all four supported MangaDex content-rating categories to avoid falsely excluding chapters.

- Original work language: **Korean (`ko`)**
- Hosted Korean chapter feed entries: **0**
- Hosted chapter feed entries in **all languages**: **0**
- Korean original-image paths and CBZ archives downloaded: **0**
- **Conclusion:** MangaDex lists this title but does not host chapter uploads in Korean or any other language. Do not run an empty MangaDex media-downloader job. A Korean original-language tag is only bibliographic metadata.

## Official English alternative

**[Tapas: Acquainted: Encounter Spin-Off](https://tapas.io/series/acquainted-encounter-spin-off/info)**

- Official English manhwa, credited to **Perilla and PAMBA**, published by Tapas Media in 2021.
- Completed, **50 episodes** available through Tapas's reading/unlocking model; some are temporarily free or locked.
- Tapas's [Read offline policy](https://help.tapas.io/hc/en-us/articles/115000415034-Read-offline) explicitly restricts downloads to playback inside the mobile app; it does **not** authorise independent CBZ, EPUB, PDF or offline files for another app.
- Tapas's official [End of Service FAQ](https://tapas.io/newsfeed/271) says access to all Tapas content and unlocked episodes ends **31 March 2027 at 23:59 PT**. The urgency is real, but the impending closure is **not** a permission grant to bypass download restrictions.

Other websites have reposted episode listings, but a third-party catalogue or online copy is not proof of publisher-granted image export rights, original fidelity or English completeness.

## What can happen next

1. Prioritise **direct author/publisher or licensor consent** or an expressly DRM-free licensed full English volume/episode export. Look for files supplied by the rights holder, not arbitrary scraper bypasses.
2. If licensed or independently authorised English images are supplied locally, import using the existing **image-folder/CBZ/ZIP** importer or verified English **DRM-free EPUB** importer. Verify actual page English text and original bytes; provide Controller-ready package without inventing episode IDs.
3. In the absence of export permission, the immediate legitimate reading option is Tapas's own app, including in-app downloads for unlocked episodes where available. These expire and do **not** migrate to Taiyou's Manga Library.
4. Continue checking first for an authorised portable English edition or rights-holder consent; until then report **blocked: official English exists, but no permitted portable download**.

The [priority title audit workflow](../.github/workflows/high-priority-mangadex-audit.yml) is metadata-only; it never promises chapter files. The [existing manga local import guide](DOWNLOAD_GUIDE.md) can package genuine user-supplied, permitted files if one becomes available.

## Next task prioritisation

The recurring Manga Retriever monitoring task now checks this title **before** Kainushi wa Akuma, Kimi no Iru Machi, Love Hina, Lovely Complex, Mado kara Madoka-chan and Nisekoi, which remain parallel workstreams. Do not block their independent permitted source checks while this item is awaiting a portable English source.
