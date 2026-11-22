# Nisekoi MangaDex exact-ID metadata audit

**Audit date:** 22 November 2026  
**Workflow run:** [44975851598](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44975851598)  
**Exact MangaDex ID:** `ce16b1c3-d6bb-41e0-8671-d8b065248ba2`

## Result

A third-party chapter tracker reported MangaDex chapter 229 for Nisekoi. The exact-ID MangaDex API check confirms that the UUID identifies the completed work through its romanised `ja-ro` title field (`Nisekoi`), but it does **not** expose an English title field.

The actual MangaDex English feed contains only **5 entries**:

- 5 distinct numbered chapter labels.
- First numbered chapter: 1.
- Highest numbered chapter: 229.
- Missing numbered chapters: **5–228**.
- No decimal extras or unnumbered entries.
- The sampled first English chapter exposes **0 original-quality and 0 data-saver page paths**.

The chapter 229 tracker listing therefore does not demonstrate a complete English MangaDex feed. The MangaDex metadata audit's earlier five-entry result is confirmed. This exact title is not a usable image source.

## Rights and media boundary

- The feed query explicitly filters `translatedLanguage[]=en`.
- The title metadata and chapter feed were queried; one first-chapter image manifest was inspected.
- **0 image bytes downloaded; 0 CBZ files created.**
- Page text was not manually reviewed.
- MangaDex/scanlation archival rights were not established.
- This result does not authorise downloading or retaining the artwork.

## Retained report

Latest metadata-only artefact:

| Field | Value |
|---|---|
| Run ID | `44975851598` |
| Artefact ID | `14735736942` |
| Name | `nisekoi-mangadex-metadata-only` |
| Size | 1,388 bytes |
| Created | 22 Nov 2026, 02:23:40 UTC |
| Expires | 29 Nov 2026, 02:23:40 UTC |
| SHA-256 | `f286e988f2a255385fc2e5fcbc309182cd70d5db5d3f88e504fd49072e93938b` |

The artefact ZIP contains only `nisekoi-mangadex-metadata.json`. No media files or private destination were involved.

## Decision

Do not implement a MangaDex image downloader for Nisekoi on this evidence. Continue to treat the official VIZ English edition as the licensed reading source; no DRM-free export route has been established. Do not repeat the old ManhuaTop probes without a meaningful upstream change.
