# Roadmap and verification status

| Milestone | Status |
| --- | --- |
| M1/M2: local import, CBZ/Controller candidates, CI | Implemented and verified |
| M3: Pepper&Carrot ep26 licensed download | Implemented; earlier real online smoke passed |
| M4: page checkpoint and recovery | Implemented with synthetic and CI tests |
| M5: approved bulk GitHub Actions + metadata-only receipts | Implemented with CI; real M5 smoke encountered upstream network failure |
| M6: Windows retrieval, verified skip-existing, consolidated ZIP | Implemented with Python CLI and Windows CMD launchers; GitHub artefact live handoff is subject to availability |
| M7: Controller + Reader live acceptance | Not implemented, candidate v1 generated |
| M8: additional authorised manga sources | Officially distributed Japanese manga identified and supported via owner-declared **local PDF import**; direct remote adapter remains pending |
| Five-title MangaKatana URL pilot | **Implemented for five exact local URLs**; one real image-containing CBZ for each Chapter 1 verified (246 pages combined); English page text, full-series coverage and source export permission unverified |
| High-priority Acquainted: Encounter Spin-Off | MangaDex title verified; **0 chapters across all languages**; Tapas reader is not an authorised portable CBZ export |
| Generalised URL acquisition | **Not implemented**; only fixed source-specific, rights-gated paths exist |
| Complete English library/Controller end-to-end | **Not verified**; requires independent Storage Controller acceptance and owner-approved private-data process |

Downloaded media is permitted only for an explicitly approved source and never committed to the public repository. A full Controller/Reader integration is not claimed.

 
For the most current source-specific evidence, follow [project handbook](PROJECT_HANDBOOK.md), [supported sources](SUPPORTED_SOURCES.md) and the linked GitHub Actions run IDs rather than inferring success from a roadmap milestone alone.
