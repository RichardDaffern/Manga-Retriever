# Unattended ReLIFE batch completion and retry

The 12 chapter-range jobs for *ReLIFE* 1–222 are automatically queued within the existing [ReLIFE Complete Numbered Series Download workflow](../.github/workflows/relife-series.yml). `max-parallel: 2`, `fail-fast: false` ensure later batches start automatically after earlier jobs finish.

The [ReLIFE Automatic Batch Recovery workflow](../.github/workflows/relife-auto-recovery.yml), stored on `main`, responds to the full-series workflow completing. It publishes a seven-day **metadata-only** completion report listing all 12 batch artefact names, what is present, and what is missing or expired.

If the original workflow fails, the recovery job requests a **failed-jobs-only rerun**, leaving successfully downloaded artefacts intact. It retries at most twice (run attempts 2 and 3) after a brief 60-second cooldown. Permanent failures remain visible rather than being silently declared successful. The recovery job uses only an Actions-write token and does not check out or execute the source workflow's branch code.

This is not independent verification of chapter identities, licence or publisher-master resolution. GitHub artefacts remain visible according to repository permissions and expire seven days after upload.

The original all-chapter run: https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44547390262
