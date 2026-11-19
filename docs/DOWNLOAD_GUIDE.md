# Local import guide

1. Use only your own or clearly authorised images. Organise as `Series/Chapter 1/001.png`, `Series/Chapter 2.cbz` or directly a `.cbz` file.
2. Run `python -m manga_retriever import --source PATH --output NEW_OUTPUT --registry PRIVATE_IDS_JSON`. Optionally supply `--rights-json PRIVATE_RIGHTS_JSON` and `--direction rtl|ltr|vertical`.
3. Run `python -m manga_retriever verify --export NEW_OUTPUT` and inspect `download_manifest.json`, candidate `inventory.json`, `catalogue.json` and CBZ files.
4. **Do not commit outputs** or upload them to a public GitHub Actions artefact. Cloud upload is disabled in the Storage Controller.

Every destination must be a new directory. To re-import an updated source, use another output path and keep the same private ID registry. Missing sequential page numbers appear as warnings, not guessed replacements. Exporting unverified partial remote chapter ranges is not implemented.
