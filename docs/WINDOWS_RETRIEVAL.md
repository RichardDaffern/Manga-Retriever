# Windows download and consolidation (M6)

M6 retrieves **only** already approved, completed, short-lived GitHub Actions exports. It is not a generic website scraper and it does not access Hugging Face.

## Set-up

1. Install Python 3.12 and [GitHub CLI](https://cli.github.com/). Run `gh auth login` and `gh auth status` once. The GitHub CLI may request a web login even for public artefacts.
2. Clone/download [Manga Retriever](https://github.com/RichardDaffern/Manga-Retriever), then `py -3.12 -m pip install -e .` inside the repo.
3. Run the **Bulk Manga Download** workflow for an approved key, currently `peppercarrot:26`. Wait for a successful artefact receipt and `downloaded_manga.json` on `main`.
4. Open **Command Prompt** inside the cloned repo and run `Download-Manga.cmd`. This retrieves the latest unexpired licence-approved artefact to `downloads/peppercarrot-26-run-<run-id>/`. Or choose `Download-Manga.cmd --run-id 123456 --key peppercarrot:26` for a specific run.
5. Run `Bundle-Manga.cmd` to create a locally verified `manga-exports.zip` containing separately named verified exports plus a SHA-256 manifest. The output ZIP must not already exist.

Direct equivalents:

```powershell
py -3.12 -m manga_retriever.retrieve download --registry downloaded_manga.json --directory downloads
py -3.12 -m manga_retriever.retrieve bundle --exports downloads --output manga-exports.zip
```

**Skip-existing:** When the destination exists, its complete Controller candidate and CBZ are verified against the metadata receipt and SHA-256 before being skipped. A corrupt existing output stops with an error; it is never silently replaced. To replace a corrupt copy, first move it outside the downloads folder and review it, then repeat the retrieval. A failed download never publishes an incomplete output.

**Expiry:** GitHub Actions artefacts are retained for seven days. The metadata registry records historical receipts, not durable storage. If the artifact expired or was deleted, rerun the allowlisted GitHub workflow; the tool intentionally does not use stale artefact links. The retrieval command requires GitHub CLI access and cannot guarantee live-source availability.

**Portability:** `manga-exports.zip` preserves original verified encoded pages, separate CBZs, Controller candidate records and provenance. Do not extract and upload through an unverified cloud tool: the Controller must validate candidate v1 independently before any owner-approved upload. No artwork or private datasets are committed to this public repository.
