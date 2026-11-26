# English manga acquisition gap register

**Reconciled:** 24 November 2026. This is a decision-ready *evidence/status register*, not a list of authorised download targets. Confirm site status and work-specific permissions again before any new acquisition.

## Historical GitHub Actions outputs, owner-private recovery not yet confirmed

| Title | Verified GitHub artifact evidence | Remaining verification |
| --- | --- | --- |
| ReLIFE | 12 live selected artifacts; jobs cover numbered 1-222 | Validate downloaded CBZ pages, English text, chapter completeness and independent owner storage |
| Love So Life | 7 live selected artifacts; jobs cover 1-106 plus 5 extras | Independently reconcile chapter labels and 111-chapter catalogue; page English and rights |
| Last Game | 3 live selected artifacts; jobs cover 1-56 | Verify bytes, language and completeness |
| Kaichou wa Maid-sama! | 5 live selected artifacts; jobs cover 1-85 | Verify bytes, language and completeness |
| Onizuka-chan and Sawarida-kun | 3 live selected artifacts; jobs cover 1-49; producer also reported decimal extras/Chapter 0 | Reconcile main versus fractional extras; verify actual files |
| Kainushi wa Akuma | 3 selected live batches; partial only | Resolve ambiguous 45 MangaDex feed versus 56 alternative-listing chapter labels; check duplicate Batch3 artifact |

Artifact IDs, expiry and sizes were [rechecked live](HISTORICAL_ARTIFACT_RECONCILIATION_20261124.md). **These historical media bytes have not been independently recovered to the owner's private disk by this audit.** A completed Actions job is not a complete locally retained English edition. Do not repeat costly source acquisitions before checking existing eligible files.

**Reconciliation, 26 November 2026:** The Storage Controller's [protected read-only smoke on 20 November](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller/actions/runs/44721448011) verified **five titles already in private canonical storage**: ReLIFE, Love So Life, Last Game, Kaichou wa Maid-sama! and Onizuka-chan and Sawarida-kun (587 chapters, 14,635 pages). Their **30 historical ZIP artefacts are not 30 missing uploads**. Kainushi wa Akuma accounts for the remaining **three selected, partial ZIP artefacts** and was not in that dated five-title snapshot. The private catalogue must be freshly rechecked before inferring any missing chapters. Download eligibility and rights are separate from technical availability.

**Targeted Kainushi preflight (read-only, no media download):** `py -3.12 -m scripts.recover_existing_manga --titles kainushi-wa-akuma --audit-only`. Existing copies require independently checked owner-local retention rights. Explicit `--titles all` remains available for justified backups, but must not be used as a missing-title upload plan.

## New titles and edition-specific source gaps

| Requested work | Actual technical evidence | Current blocker / decision |
| --- | --- | --- |
| Kimi no Iru Machi | MangaKatana early/middle/end pilot decoded 149 image pages across 6 CBZs; exact MangaDex English feed 0 | Page text language and portable archive permission not independently established; no retained authorised full series |
| Love Hina | MangaKatana 6 CBZs, 135 pages; MangaDex 2 English feed entries with 0 sampled hosted page paths | Potential publisher-authorised original-format purchase route, contingent on owner entitlement and actual file format; no confirmed export rights for MangaKatana |
| Lovely Complex | MangaKatana 6 CBZs, 307 pages; MangaDex 66 numbered English records but 0 sampled hosted page paths | Standard versus coloured edition must remain separate; language and rights unresolved |
| Mado kara Madoka-chan | MangaKatana 6 CBZs, 60 pages; MangaDex English feed 0 | English edition/translation coverage and file retention rights unresolved |
| Nisekoi: False Love | MangaKatana 6 CBZs, 135 pages; exact MangaDex 5 English entries with 0 sampled hosted page paths | Official Shonen Jump/VIZ reading is not CBZ permission; English text and portable source unverified |
| The Fairytale-like You Goes on the Assault | One real 8-page MangaKatana Chapter 1 CBZ pilot; 42 main chapters in listing, MangaDex has extra labels | Creator restrictions make external archive/translation use inappropriate without specific permission |
| Acquainted: Encounter Spin-Off | Exact MangaDex UUID `90f7c7a6-b759-4afb-b1cb-1af4660df307` has **0 chapters in every language**; 50 official English Tapas episodes are app-bound | No verified authorised portable export; do not use an empty MangaDex feed or attempt app/DRM extraction |

Technical image pilot counts above describe **ephemeral decoded pages that were deleted from public runners**, not retained media. See [fifteen-job pilot results](HISTORICAL_MANGA_ARTIFACT_RECOVERY.md), [new MangaDex audit](NEW_TARGET_MANGADEX_METADATA_AUDIT_20261122.md), and [source matrix](SUPPORTED_SOURCES.md). These results do not independently prove English page text.

## Recommended action order

1. **Recover/reconcile existing eligible owner copies first.** The 33 pinned artifacts expire 26–27 November 2026. Use the locally run, authenticated private recovery tool; verify what was already retained.
2. **Hand off only validated owner-authorised material.** Validate private candidate v1 through both Retriever and Storage Controller. Preserve stable IDs and never publish third-party pages through this public repository.
3. **Review English image samples and chapter gaps per exact title/edition.** Record source ID, actual chapter labels, page counts, fractional extras, original-versus-saver quality and discrepancies. Do not substitute a successful metadata or pilot run.
4. **Prefer explicitly licensed creator or purchaser-provided DRM-free images/CBZs/EPUBs/PDFs.** Verify each work's specific terms and the purchaser's file entitlement before using a source; do not evade paywalls, site blocks or access controls.
5. **Separate storage and reading acceptance.** No newly acquired title counts as integrated until the Controller's independently approved, backed-up write and the Library's authenticated read-back are verified.

**Stop conditions:** No portable source rights, missing original-language/English verification, no actual image bytes, absent chapter coverage, or no authenticated private retention. The correct outcome is a documented blocker, not a fabricated full-series download.
