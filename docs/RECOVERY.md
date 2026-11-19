# Recovery and data integrity

M4 (implemented): Pepper&Carrot Episode 26 uses a persistent, private page checkpoint named `.<output-name>.checkpoint/` alongside the export. The index is schemaVersion 1 with an immutable source URL, ordered six-page URL plan, and SHA-256 and byte size for completed images. Each image is fully decoded and saved via fsync and atomic rename before the index is updated. Repeat the same command and registry after interruption. Valid cached pages are revalidated, missing or corrupt pages are downloaded again, and no partial Controller candidate or CBZ is published. An exclusive lock forbids concurrent writes; inspect a stale lock rather than deleting it automatically. A changed source plan or malformed index refuses to resume. The official licence and source page are fetched again on every retry.

The checkpoint directory is generated scratch media and is deleted **only after** the verified export is published. The verified export and private identity registry are never overwritten. Files stranded between page write and index commit are treated as untrusted and fetched again, not marked completed. Back up the private `ids.json` before renaming/moving input paths. Run `python -m manga_retriever verify --export DIR` before trusting a completed export.

M5 bulk scheduling and metadata-only registries are planned. No unsupported source or cloud upload is activated.

## M5 batch recovery

Use the `manga-batch-status-<run-id>` artefact to see completed and missing allowlisted keys. Successful licensed exports remain separately retrievable for seven days; a failed sibling cannot remove them. The finalisation stage records completed artefact receipts even if another job fails, and its status check correctly reports the incomplete batch as failed. To retry missing keys, run **Bulk Manga Download** again with their comma-separated identifiers. The current only approved key is `peppercarrot:26`. Do not infer that an expired or manually deleted GitHub artefact still exists just because its historical registry entry is present. No automatic deletion of remote media or owner originals occurs.
