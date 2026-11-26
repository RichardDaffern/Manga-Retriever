# Retriever to Manga Storage Controller and Library integration

**Reconciled:** 24 November 2026. This document separates the Retriever's local output from the Controller's production deployment and the Library's authenticated media gateway.

## Ownership and current integration state

| Component | What it owns | Verified state |
| --- | --- | --- |
| [Manga Retriever](../README.md) | Authorised acquisition, safe original-image/CBZ packaging, Controller candidate v1 and local checks | Implemented; Retriever's offline tests and earlier main CI passed |
| [Manga Storage Controller](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller) | Independent candidate validation, immutable IDs, private HF canonical metadata/media, backups and revision-guarded writes | Canonical v1 and private HF operations are implemented. The Controller reported read-only validation on 20 November 2026; **current production dataset state was not re-read here** |
| [Manga Library](https://github.com/AdityaSreevatsaK/Taiyous-Manga-Library) | Authenticated Cloudflare Functions/private media gateway and the reader's catalogue/progress UI | A private gateway exists in the Library. A Retriever candidate is **not** automatically displayed by the reader |

**Reconciliation, 26 November 2026:** The Storage Controller's [protected read-only smoke on 20 November](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller/actions/runs/44721448011) verified **five titles already in private canonical storage**: ReLIFE, Love So Life, Last Game, Kaichou wa Maid-sama! and Onizuka-chan and Sawarida-kun (587 chapters, 14,635 pages). Their **30 historical ZIP artefacts are not 30 missing uploads**. Kainushi wa Akuma accounts for the remaining **three selected, partial ZIP artefacts** and was not in that dated five-title snapshot. The private catalogue must be freshly rechecked before inferring any missing chapters. Download eligibility and rights are separate from technical availability.

**Targeted Kainushi preflight (read-only, no media download):** `py -3.12 -m scripts.recover_existing_manga --titles kainushi-wa-akuma --audit-only`. Existing copies require independently checked owner-local retention rights. Explicit `--titles all` remains available for justified backups, but must not be used as a missing-title upload plan.

**Correction to older guidance:** The Controller's HF capability is **not categorically disabled**, and the Library **does** have a private asset gateway. What remains unverified is the full, owner-approved Retriever candidate → Controller production upload → Reader visibility workflow for a specific newly acquired title.

Reference contracts: [Controller data contracts](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller/blob/master/docs/DATA_CONTRACTS.md), [Controller validator](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller/blob/master/src/taiyou_manga/builder.py), [Reader types](https://github.com/AdityaSreevatsaK/Taiyous-Manga-Library/blob/master/src/domain/types.ts).

## Candidate v1 handover

The Retriever's `import_local` output includes:

```text
export/
  chapters/ch_<opaque-id>.cbz
  download_manifest.json
  controller_candidate/
    catalogue.json
    inventory.json
    manifests/ch_<opaque-id>.json
    assets/manga/mng_<opaque-id>/ch_<opaque-id>/pg_<opaque-id>.<original-ext>
    rights.json  # optional owner declaration; private, never commit
```

The Controller independently checks `controllerCandidateVersion: 1`, `mediaKind: manga`, immutable `mng_*, ch_*, pg_*` identifiers, chapter sequences, per-page hashes, decoded image dimensions/MIME and absence of unexpected assets. It reads the local `controller_candidate/` directory. It does **not** use the separate `chapters/` CBZ files or `download_manifest.json` as a source of truth.

The Retriever rejects repeated identical pages in one chapter; the Controller can optionally support duplicates in separate import modes. This is a deliberately stricter Retriever input policy, not permission to silently change page-ID derivation. Preserve the private identity registry when reimporting or renaming source paths.

## Independent synthetic cross-repository acceptance

`tests/test_controller_acceptance.py` exercises actual `manga_retriever.importer.import_local` output with the real Controller's `taiyou_manga.builder.verify_bundle`. It verifies two synthetic chapters, original-byte SHA-256 and deterministic page identities, stable reimport, corruption rejection, orphan rejection and the separate rights-declaration indicator. It also previews, explicitly approves and reads back a **disposable local MockStorage snapshot** with revision-conflict checks; this never calls HF or the Library. No real manga files or credentials are involved.

The dedicated `controller-candidate-contract` job in [CI](../.github/workflows/ci.yml) installs the public Controller repository **at commit** `f6bfc82b335c415dac55512c4dc4d640a5883392` and runs the acceptance tests. Pin changes must be deliberately reviewed against the current Controller contract, not silently updated.

Run locally in a disposable Python 3.12 environment:

```bash
python -m pip install -e .
python -m pip install "git+https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller.git@f6bfc82b335c415dac55512c4dc4d640a5883392"
python -m unittest tests.test_controller_acceptance -v
```

For an **owner-authorised private** candidate, both validations must succeed:

```powershell
py -3.12 -m manga_retriever verify --export "C:\\Manga\\export"
py -3.12 -m taiyou_manga verify --bundle "C:\\Manga\\export\\controller_candidate"
```

A passing synthetic contract check is evidence of local package compatibility **only**. It is not a production HF upload, a verified backup, a rights clearance, English-page verification or Library display.

## Production handoff is separately gated

1. Inspect private local files and rights evidence (a `rights.json` declaration alone does not establish permission), and manually review English page text.
2. Independently validate every candidate with the Controller, review existing immutable IDs and conflict-free dry-run against the **current** private HF revision. Never regenerate IDs just because local paths moved.
3. Verify original-media independent backup and obtain Controller-specific approval of the exact upload preview, as required by its operational contract.
4. Let the Controller upload validated original images before publishing catalogue references. Read back the new revision and verify the Library's owner-authenticated catalogue/pages. Roll back through Controller procedures if required.

**Do not** have Retriever write directly to Hugging Face or publish private manga/rights records through public GitHub Actions. No production uploads, migration or private Library configuration changes occur in the cross-repository CI job.
