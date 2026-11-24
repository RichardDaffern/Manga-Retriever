# Public third-party manga workflow quarantine

**Date:** 24 November 2026. **Scope:** public `RichardDaffern/Manga-Retriever` repository. The historical GitHub Actions runs and their existing artifact IDs remain unchanged.

## Why the legacy jobs are blocked

A public workflow uploading third-party manga chapter CBZs or images into a GitHub Actions artefact can make copyrighted artwork retrievable outside the intended private library. Earlier executions and owner retention intent are **not** independent redistribution permission. Some old jobs also automatically retry public manga media pipelines. Re-running those workflows risks republishing without current work-specific rights verification.

This change deliberately disables the affected download and automatic retry jobs with an explicit `if: ${{ false }}` guard. It does not delete GitHub history, change the historical artifact manifest, revoke previously issued artefacts, change any private Hugging Face data, or alter the independently licensed Pepper&Carrot workflow.

## Disabled jobs

| Workflow | Blocked job |
| --- | --- |
| `relife-series.yml` | `download` |
| `relife-download.yml` | `download` |
| `love-so-life-download.yml` | `verified-chapter-batches` |
| `love-so-life-extras-download.yml` | `verify-five-extras` |
| `three-manga-download.yml` | `download-and-verify` |
| `onizuka-recovery-download.yml` | `download-onizuka` |
| `kainushi-available-download.yml` | `verified-partial-source-batches` |
| `relife-auto-recovery.yml` | `retry-failed`, while the metadata-only report job remains |
| `three-manga-recovery.yml` | `automatic-retry` |
| `additional-manga-recovery.yml` | `retry-failed` |

An offline [regression test](../tests/test_workflow_quarantine.py) checks that these job gates stay disabled. This is a defence against a future edit accidentally restoring public media publication, **not** a guarantee that GitHub will prevent rerunning an older historical commit's workflow. Do not use historical-run reruns as a workaround.

## Supported safe alternatives

- For existing historical artifacts, run the [verified private owner-local recovery](HISTORICAL_MANGA_ARTIFACT_RECOVERY.md) on a private computer before their 26–27 November expiry. The new `--audit-only` mode checks metadata without downloading.
- For additional acquisitions, prefer explicitly licensed/creator-provided assets and owner-provided DRM-free files, with per-work rights, actual English page review, original-byte validation, bounded private runs and secure storage.
- The fixed `peppercarrot:26` licence-approved public workflow remains available. JSON-only metadata and ephemeral technical report workflows are not disabled by this change.
- The Storage Controller alone may take validated, authorised private bundles through its separately approved revision-guarded upload and Library read-back process.

**To lift a quarantine:** review the exact title, licence, who owns the translation, permitted redistribution audience, source URL, specific media outputs, workflow publication destination and rights evidence. Prefer a new private, owner-controlled acquisition mechanism rather than re-enabling a public CBZ uploader.
