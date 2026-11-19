# Love So Life and Kainushi wa Akuma: source quality / permissions gate

**Goal:** Determine whether the English chapter inventories are sufficiently complete for a high-quality, small-scale pilot. This is intentionally a **source-readiness check**, not a new public manga media download.

## Sources and documented rights

- **MangaDex official API policy:** https://gitlab.com/mangadex-pub/mangadex-api-docs/-/blob/main/index.md . API integrations must credit MangaDex and scanlation groups, honour scanlation-group removal requests, and not run ads or paid services. It is **not** a creator, publisher or scanlator copyright licence for bulk archiving and public sharing of chapter images.
- **Love So Life:** Japanese publication by [Hakusensha](https://www.hakusensha.co.jp/comicslist/46650/) (17 volumes); an [external chapter list](https://mangapill.com/manga/2648/love-so-life) labels 1–106 plus decimal bonus chapters. [Earlier exact MangaDex metadata](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44590570263) found 106 integer-numbered English chapters, five decimal bonuses, 119 feed entries and 50 original-image paths in one manifest. Counting distinct labels suggests the 111 advertised chapters may include five bonus items; **that remains an inference**, not edition authentication.
- **Kainushi wa Akuma:** Japanese title by Eiri Kaji, [OniSaga chapter index](https://onisaga.com/manga/kainushi-wa-akuma) lists integer and decimal/subchapter releases through 25.5 and multiple volumes. Earlier MangaDex metadata had 45 English feed entries with decimal-heavy labels, versus a larger external English index. Integer chapter coverage is the wrong completeness metric for this serialisation.

## Automated verification

The [readiness workflow](../.github/workflows/love-kainushi-readiness.yml) obtains the exact English title feeds, enumerates **all raw chapter labels** without merging decimal-numbered entries into integer chapters, identifies duplicate releases, blank labels, missing integer gaps and external-reader records. It samples first, middle and last English chapter **image manifests** for source-original and data-saver filename counts/extensions, without fetching any page image bytes.

The report explicitly records **zero artwork downloads** and **unverified publisher-master image resolution**. It never stores raw image URLs, client credentials, or media.

## Release gate

Before any new automatic manga upload to a public GitHub Actions artefact, confirm creator/publisher/scanlator permissions for the target material, inspect the full numbered and bonus chapter inventory, and compare actual page dimensions/fidelity against the available source (privately, where authorised). Publisher-original quality cannot be measured from an API manifest.

**No permission to publish fan translations or original artwork has yet been verified.** No public media workflow is enabled for these two titles. Reader and Controller production repositories are unchanged.
