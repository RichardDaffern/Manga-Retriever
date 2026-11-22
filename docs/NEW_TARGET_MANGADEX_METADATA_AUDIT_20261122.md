# New-target MangaDex metadata-only audit

**Audit date:** 22 November 2026  
**Workflow:** [44980421781](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44980421781)  
**Branch commit:** `e821912bb01904f12b60a8984eee127d058ef107`

## Scope and safety

This audit covers the five new targets not already checked by the separate Nisekoi exact-ID audit:

- Kimi no Iru Machi
- Love Hina
- Lovely Complex
- Mado kara Madoka-chan
- The Fairytale-like You Goes on the Assault

It uses exact title/alias matching, paginated MangaDex `translatedLanguage=en` feeds, and at most one first-chapter at-home image-path manifest per exact edition. It retrieves no image bytes, creates no CBZs and does not assert archival rights.

**Result:** five exact title matches; English feed metadata exists for four exact editions across three titles. This is not four complete series or four authorised sources.

## Results

| Target / exact edition | MangaDex ID | English feed | Numbered coverage | First original/data-saver paths | Decision |
|---|---|---:|---|---:|---|
| Kimi no Iru Machi | `8f6c0971-2add-4a63-b238-74c033064502` | 0 | None | Not queried | No English feed |
| Love Hina | `b3fe7c22-0045-439a-9b74-82d43a19eeb4` | 2 | 1-2 | 0 / 0 | Feed entries do not have MangaDex-hosted page paths |
| Lovely Complex, standard edition | `7a1c6e41-6c2d-401e-90fe-baccb637a63e` | 71 | 66 numbered, 1-66; 2 fractional extras | 0 / 0 | No hosted page paths |
| Lovely Complex, Digital Colored Comics | `7b273ab1-42cb-4004-8ffd-1c6f580cc107` | 0 | None | Not queried | No English feed |
| Mado kara Madoka-chan | `1d8d129f-8566-49b8-8d81-feda6444cc7b` | 0 | None | Not queried | No English feed |
| Fairytale-like You, standard edition | `6cc85df7-e44b-4fa1-97f2-be04430cc570` | 84 | 42 numbered, 1-42; 33 fractional extras | 8 / 8 | Metadata and a page manifest exist, but rights are not established |
| Fairytale-like You, fan-coloured edition | `d8ad977d-cfb3-477a-93b6-308025b250c2` | 1 | Chapter 30 only; 1-29 absent | 10 / 10 | Incomplete metadata; rights are not established |

### Interpretation

- **Kimi no Iru Machi:** the exact Japanese title exists, but its English feed is empty.
- **Love Hina:** two English-labelled chapter records exist, but the sampled first chapter has zero original and zero data-saver page paths. This is not a working image source.
- **Lovely Complex:** the standard edition's feed metadata covers all 66 numbered chapters and two fractional extras, but its sampled first chapter has zero hosted page paths. The separate digital-coloured edition has no English feed. The audit deliberately did not choose between editions automatically.
- **Mado kara Madoka-chan:** MangaDex has an English title metadata field, but zero English chapter-feed entries. An English title label is not proof of English pages.
- **Fairytale-like You:** the standard edition lists 84 English feed entries, including 42 numbered chapters and 33 fractional extras; its first-chapter manifest reports eight paths. The fan-coloured edition lists only one English chapter, chapter 30. These are community translation records, not authorised publisher exports. The creator's public profile asks that the work not be reposted and that translations not be published on overseas sites: [Kazutake Hazano](https://twitter.com/teigi_3). Do not download or archive these uploads without explicit permission.

## Nisekoi cross-reference

The separate exact-ID audit [44975851598](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44975851598) found:

- Exact title ID: `ce16b1c3-d6bb-41e0-8671-d8b065248ba2`.
- Five English feed entries and five distinct numbered chapter labels.
- First numbered chapter 1, highest 229, with chapters 5-228 absent from the feed.
- The sampled first chapter exposed zero original and zero data-saver page paths.
- No image bytes were downloaded and no rights to archive or redistribute were verified.

## Retained report

The workflow retained one JSON-only artefact:

| Field | Value |
|---|---|
| Run ID | `44980421781` |
| Artefact ID | `14737930636` |
| Name | `new-target-mangadex-metadata-only` |
| Size | 2,501 bytes |
| Created | 22 November 2026, 03:24:28 UTC |
| Expires | 29 November 2026, 03:24:27 UTC |
| ZIP SHA-256 | `59d6881259dd7b63efc6dca229639e7e3af5036b6223598c411d5b336b59f5e5` |

The ZIP contains only `new-target-mangadex-metadata.json`. No images, archives, personal files or private destination were involved.

## Decision

MangaDex is **not an authorised acquisition source** for these titles on the evidence available. Several entries have metadata but no hosted original image paths; the one title with a non-empty image manifest is subject to unresolved rights and explicit creator restrictions.

- Image bytes downloaded: **0**
- CBZ files created: **0**
- Rights verified: **false**
- Eligible media-download targets: **0**

Do not implement or trigger MangaDex image downloads from these results. Continue seeking publisher/creator-authorised DRM-free exports. Do not repeat the failed ManhuaTop probes without a meaningful upstream change.
