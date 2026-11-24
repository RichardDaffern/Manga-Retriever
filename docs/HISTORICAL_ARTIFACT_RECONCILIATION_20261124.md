# Historical manga artefact availability reconciliation

**Checked:** 24 November 2026 against live GitHub Actions metadata. **No media bytes downloaded or read in this audit.** This document is a *public-safe metadata receipt*, not verified owner retention, a media quality certificate, proof of English language or permission to distribute.

| Title | Pinned | Unexpired | Approx. ZIP size (GiB) | Earliest expiry (UTC) |
| --- | ---: | ---: | ---: | --- |
| ReLIFE | 12 | 12 | 1.25 | 2026-11-26T15:01:32Z |
| Love So Life | 7 | 7 | 1.92 | 2026-11-26T19:32:20Z |
| Last Game | 3 | 3 | 0.85 | 2026-11-26T19:51:54Z |
| Kaichou wa Maid-sama! | 5 | 5 | 1.25 | 2026-11-26T18:55:12Z |
| Onizuka-chan and Sawarida-kun | 3 | 3 | 0.07 | 2026-11-27T04:39:35Z |
| Kainushi wa Akuma | 3 | 3 | 0.69 | 2026-11-26T19:45:10Z |
| **Total** | **33** | **33** | **6.03** | |

- Exact original IDs, corresponding run IDs and ranges: [pinned historical manifest](../scripts/historical_manga_artifacts_20261120.json).
- 1 additional non-pinned artefact appeared in the checked runs: `Kainushi-Available-English-Batch3` (ID `14569604628`, run `44597755913`). The non-pinned Kainushi Batch3 is omitted intentionally; do not add it without verifying duplication.
- Availability here is only GitHub's `expired: false` metadata at the check time, *not* a guarantee that a future download succeeds. The deadline is **26 November 2026** for most files and **27 November 2026** for Onizuka.
- The source repository and artifacts are public. Public access does not grant rights to redistribute third-party artwork or to transfer it into an unrelated private dataset.

## Required private recovery operation

The owner must run an authenticated recovery on an **owner-controlled private Windows disk**, first checking existing private holdings and permissions for each title. The existing [recovery script and guide](HISTORICAL_MANGA_ARTIFACT_RECOVERY.md) pin all 33 IDs, verify ZIP/CBZ safety, decode pages, check hashes, retain good previously downloaded sets and avoid overwriting files. For a private owner-authorised inventory:

```powershell
Recover-Existing-Manga.cmd "C:\\Manga\\Recovered" all 3
```

**Do not run the above in public CI** and do not upload its output to a public Actions artefact. The authenticated local recovery status file, actual private bytes and Controller candidate acceptance must be verified separately. This repository cannot inspect an owner's pre-existing local holdings via GitHub metadata. **No private recovery is certified by this receipt.**

## Follow-up boundaries

1. Reconcile the local `historical-recovery-status.json` with the intended chapter labels, including fractional/extras and potentially duplicated Kainushi Batch3.
2. Compare actual SHA-256/page counts and sampled page language before considering title completeness. Record mismatches, never infer completeness from job ranges.
3. Only accept a bundle with the separate Storage Controller validator after source permissions and local identity registry have been reviewed. A passing test does not authorise production HF writes.
