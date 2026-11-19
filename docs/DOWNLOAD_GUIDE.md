# Local import guide

1. Use only your own or clearly authorised images. Organise as `Series/Chapter 1/001.png`, `Series/Chapter 2.cbz` or directly a `.cbz` file.
2. Run `python -m manga_retriever import --source PATH --output NEW_OUTPUT --registry PRIVATE_IDS_JSON`. Optionally supply `--rights-json PRIVATE_RIGHTS_JSON` and `--direction rtl|ltr|vertical`.
3. Run `python -m manga_retriever verify --export NEW_OUTPUT` and inspect `download_manifest.json`, candidate `inventory.json`, `catalogue.json` and CBZ files.
4. **Do not commit outputs** or upload them to a public GitHub Actions artefact. Cloud upload is disabled in the Storage Controller.

Every destination must be a new directory. To re-import an updated source, use another output path and keep the same private ID registry. Missing sequential page numbers appear as warnings, not guessed replacements. Exporting unverified partial remote chapter ranges is not implemented.

## Licensed Pepper&Carrot pilot

Use `python -m manga_retriever peppercarrot --episode 26 --output OUTPUT --registry IDS`. Only the official six high-resolution English pages are allowed. Network errors may be retried within the same invocation; a failed or incomplete episode produces no published output. Source rights/attribution and per-page source URLs are stored in the export. Run `python -m manga_retriever verify --export OUTPUT` before handing `OUTPUT/controller_candidate` to the Controller for *local* inspection. Hugging Face uploads remain disabled. The GitHub Actions `Single Manga Download` workflow is manual, short-lived artefact delivery, not private storage.

## Bulk Manga Download (M5)

Open **Actions > Bulk Manga Download > Run workflow**, with `selection=peppercarrot:26`. Only approved identifiers are accepted (not arbitrary URLs). Each job yields an independently downloadable, original-byte verified and attributed licensed export. Completed artefacts expire after seven days; the metadata-only `downloaded_manga.json` keeps historical results without duplicating media in Git. If a batch partially fails, inspect the `manga-batch-status-<run-id>` artefact and run the missing approved keys again. Parallel batches become useful when additional licensed sources pass separate approval; for now just Episode 26 is enabled. Storage Controller uploads remain disabled.

## Retrieve approved GitHub Actions artefacts to Windows

After the selected workflow finishes and a verified receipt has been committed to `downloaded_manga.json`, run `Download-Manga.cmd` inside a Python 3.12 checkout with authenticated GitHub CLI. The command retrieves only approved named GitHub Actions artefacts, checks source provenance and CBZ SHA-256, and atomically publishes new folders. It skips valid existing downloads and rejects corrupt copies without overwriting. `Bundle-Manga.cmd` packages separately verified exports into an integrity-checked ZIP. Artefacts expire after seven days. See [Windows Retrieval](WINDOWS_RETRIEVAL.md).
