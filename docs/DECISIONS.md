# Decision record

- 2026-11-19: Start with local authorised images and source research; do not enable arbitrary website download or MangaDex image archival.
- 2026-11-19: Preserve encoded page bytes, verify full decode, package standard CBZ and separate Controller candidate v1.
- 2026-11-19: Store stable IDs privately by input-source path; no title-derived keys for the Reader. Path-rename reconciliation remains a manual migration.
- 2026-11-19: Keep HF writes disabled in the Controller. No production data and no source site media in Git.
- 2026-11-19: Python 3.12, stdlib unittest plus Pillow; Windows and Linux synthetic CI matrix.
- 2026-11-19: M5 uses verified artefact receipts and a metadata-only public registry; simultaneous matrix jobs never push to main. The finaliser reconciles results against latest main with bounded retries and reports missing jobs separately. Download permissions remain a per-adapter allowlist, currently a single CC BY 4.0 Episode 26.
