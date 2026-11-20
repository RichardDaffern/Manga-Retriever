# Manga publication metadata enrichment: integration handover

**20 November 2026.** Retriever produces a **review-only** source metadata sidecar for existing downloaded manga. The Storage Controller and Manga Library own private catalogue reconciliation, cover storage, front-end rendering and data migration.

## Root cause and current cross-app contract

1. Retriever's `manga_retriever/importer.py` originally defaulted `aliases: []`, `creators: []`, `tags: []`, `publicationStatus: "unknown"` and did not populate `synopsis` or covers. Its `epub_import.py` only took `dc:title`, language and image bytes.
2. The Storage Controller's `src/taiyou_manga/builder.py` also creates entries with empty creator and tag arrays, with status `unknown`. It must be changed independently to **preserve and reconcile** any publication metadata instead of discarding it.
3. Manga Library `src/domain/types.ts` and `src/domain/validation.ts` support `creators`, `tags`, optional `synopsis`, `publicationStatus`, `aliases`, but have **no private cover-asset path field**. `src/App.tsx` uses decorative placeholder cover artwork and labels unknown creators. Controller and Library must agree on one new validated optional cover field, e.g. `coverAssetPath`.

## Retriever now supplies (review-only, no private writes)

`manga_retriever/publication_metadata.py` produces **one JSON per selected title** from fixed, verified MangaDex metadata endpoints. It fails closed if the source ID/title differs from the approved title. Five pinned works:

| Key | Title |
| --- | --- |
| `relife` | ReLIFE |
| `maid-sama` | Kaichou wa Maid-sama! |
| `last-game` | Last Game |
| `love-so-life` | Love So Life |
| `onizuka-sawarida` | Onizuka-chan and Sawarida-kun |

[LIVE ACTIONS: Five source-identity checks passed, 20 November 2026](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44701899805).

Every title returned **at least one creator, an English synopsis, English genre/theme tags and a cover reference**. Author/artist relationships are recorded with their roles. Publication status is a source-declared candidate only and can be wrong. The summary includes missing field names and does not invent missing values.

**Important:** The cover is a URL/reference record with `assetDownloaded: false` and `rightsClearedForRedistribution: false`. It is **not an image**, and no image byte rights or permitted HF storage have been established by this audit. The metadata job does not download or publish artwork.

### Review-only sidecar shape

```json
{
  "schemaVersion": 1,
  "mediaKind": "manga",
  "candidateType": "publication-metadata",
  "match": {
    "source": "MangaDex",
    "sourceMangaId": "fixed API UUID",
    "canonicalTitle": "ReLIFE",
    "aliasesForMatch": ["ReLIFE"],
    "doesNotContainPrivateMangaId": true
  },
  "metadata": {
    "title": "ReLIFE",
    "aliases": [],
    "creators": ["Source creator name"],
    "creatorRoles": [{"name": "Source creator name", "role": "author", "sourceId": "source UUID"}],
    "tags": ["Romance"],
    "synopsis": "English source synopsis",
    "publicationStatus": "completed"
  },
  "coverCandidate": {
    "sourceUrl": "https://uploads.mangadex.org/covers/.../source-file.jpg",
    "sourceCoverId": "source UUID",
    "assetDownloaded": false,
    "rightsClearedForRedistribution": false,
    "status": "reference-only"
  },
  "provenance": {
    "sourceUrl": "https://mangadex.org/title/...",
    "sourceApiUrl": "https://api.mangadex.org/manga/...",
    "sourceEditionMatched": true,
    "operatorReviewRequired": true,
    "replaceManualMetadata": false,
    "coverFileDownloaded": false
  },
  "missing": []
}
```

**This example is illustrative**: use the actual exact JSON artefacts, not example names or source IDs.

### Generate review records (GitHub Actions preferred)

Use [English Manga Publication Metadata Audit](../.github/workflows/publication-metadata.yml) and select **Run workflow**. Its five jobs independently write `metadata-review-<slug>` artefacts with seven-day retention. To generate one locally:

```powershell
py -3.12 -m manga_retriever.publication_metadata --slug relife --output "metadata-candidates\relife.json"
```

### Apply to a new authorised local import (explicit opt-in)

```powershell
py -3.12 -m manga_retriever import --source "C:\Manga\ReLIFE" --output "C:\Manga\verified" --registry "C:\Manga\ids.json" --metadata-json "metadata-candidates\relife.json"
py -3.12 -m manga_retriever verify --export "C:\Manga\verified"
```

The command validates the pinned source ID and the imported title, and inserts supported publication fields into a **new**, single-series Controller v1 candidate. It **does not** overwrite an existing export, change immutable IDs, alter page data, fetch the cover or migrate a private dataset. EPUB imports also accept `--metadata-json` along with their existing authorisation flag.

## Storage Controller session: required implementation

**Priority P0:** Integrate and backfill catalogue metadata in the **private** HF dataset, using its existing canonical `data/library.json`, without changing chapter/media IDs or redownloading manga.

- Validate the actual source sidecar identity and reconcile it with the **existing** opaque manga ID, not merely an ambiguous title; present conflicts for owner review.
- Apply a **field-by-field, non-destructive merge**: retain existing nonempty/manual creator, tags, synopsis, status and title unless the owner explicitly approves replacing them. Never overwrite with null/unknown/empty.
- Differentiate **publisher publication status** from user reading shelves (Finished etc).
- Revise Controller schema to store and validate a private `coverAssetPath` (exact naming agreed with Library). Acquire actual cover only with appropriate permission, create its private asset and integrity metadata, and never use public remote URLs as permanent paths.
- Support a **preview CSV/JSON**, provenance report, validation, dry-run, revision-based optimistic concurrency, backup and rollback. Preserve catalogue contents, chapter manifests, page asset paths and any existing manual information.
- Implement an optional metadata-only update path for existing titles. The user must not have to download full manga again.
- Add tests for absent metadata, unmatched/ambiguous titles, conflicting manual fields, concurrent updates and zero image/ID modification.

## Manga Library session: required implementation

**Priority P0:** Render metadata arriving from the canonical private HF catalogue without changing reading UX.

- Extend `src/domain/types.ts` and `src/domain/validation.ts` with the **same optional private cover field** chosen by Controller.
- Update the authenticated private media gateway to return validated cover bytes/URLs with no leaked HF credentials; add caching and offline fallback rules.
- Replace `src/App.tsx` decorative cover placeholder with actual cover artwork **when a verified cover asset exists**, otherwise retain the existing tasteful placeholder.
- Render author and artist names, synopsis, tags and actual publication status, and keep personal ratings/tags/shelves separate from the canonical publisher fields.
- Preserve ribbons, themes, progress, immutable route IDs, collections, offline images and responsive layouts.
- Test cloud refresh, missing/corrupt cover fallback, private access, reading continuity and mobile display.

## Definition of done

- At least the five previously retrieved English titles have creator, synopsis, tags and publication-status candidates available for review.
- Controller can safely attach correctly matched source metadata to existing entries in `data/library.json` without moving any chapter/media files or changing IDs.
- Legitimately stored covers display correctly in Library, with private access and graceful fallbacks.
- User-edited fields never get erased, and catalogue updates are previewable, backed up and revision guarded.
- Data is verified end to end before declaring the metadata issue resolved.

**Not completed by Retriever:** downloading source cover images, modifying HF, reconciling live catalogue entries or updating the Manga Library UI. Those belong to the two parallel sessions and need agreement on the cover field.
