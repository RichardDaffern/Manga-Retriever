# ReLIFE high-quality English CBZ: private Windows pilot

**Current status:** Ready-to-run local integration with existing `mangadex-downloader==3.1.4` and a **synthetically tested** integrity audit. **The live MangaDex API confirmed 240 English chapter feed entries on 19 November 2026 (metadata only); no real chapter image download has been demonstrated from this project.** Source availability and the legality/permission of locally retaining the particular scanlation must be assessed first. This does not enable a download on public GitHub Actions, do any DRM or regional bypass, or upload content to Hugging Face.

## Confirmed targets and quality

- Manga: *ReLIFE*, by YayoiSo, [MangaDex listing](https://mangadex.org/title/6e3553b9-ddb5-4d37-b7a3-99998044774e/relife).
- Japanese official publisher: [15 full-colour Japanese volumes on BookLive](https://booklive.jp/product/index/title_id/20006421/vol_no/001), which may be higher fidelity than the English uploads and may have download/DRM limits.
- English: MangaDex English uploads. This wrapper **does not use `--use-compressed-image`**, so the client should request the standard full-quality `data` images, not the lower-resolution `data-saver` images. That is *the highest MangaDex-uploaded quality*, not a guarantee of original art resolution.
- The authorised [Coolmic ReLIFE](https://coolmic.me/titles/631) English reader offers some chapters for free and more through purchase. An offline/export option is not confirmed.

## Windows pilot (first two numbered chapters)

From a cloned checkout of `RichardDaffern/Manga-Retriever` in Windows PowerShell:

```powershell
py -3.12 -m pip install -e .
py -3.12 -m pip install mangadex-downloader==3.1.4
.\Download-ReLIFE.cmd pilot "C:\Manga\ReLIFE"
```

The launcher asks you to confirm that you've reviewed MangaDex and the relevant scanlation groups' terms for this private use. It then runs a **fixed-title**, English, original-upload-image request with bounded HTTP retries and a two-second delay, invoking the installed Python module directly (no Windows `PATH` configuration required). The output is stored only on your laptop and is never committed or uploaded by this workflow. The CLI uses separate CBZs for chapters, not lossy PDFs.

On success, inspect `C:\Manga\relife_quality_audit.json`: it includes each CBZ file's SHA-256, page size/hash, page dimensions and exact count. Full integrity verification does **not** mean an uploader provided the entire series. It does not compare all scans with a publisher master.

## Full numbered series (if pilot is good)

```powershell
.\Download-ReLIFE.cmd full "C:\Manga\ReLIFE"
```

This selects chapters **1–222** where English uploads are available. Extra/decimal chapters, alternate groups, missing uploads and later revisions may not be included. The tool never labels the entire series complete without an independent chapter-level source check. The third-party client manages interrupted requests and stored files; the local audit rejects corrupt or incomplete CBZs. Repeat only within the source's applicable limits. If the downloader exits with an error, partial local files remain for inspection and the tool returns failure, never a false success.

To recheck existing CBZs offline without network access:

```powershell
py -3.12 -m manga_retriever.relife --mode audit --output "C:\Manga\ReLIFE"
```

## Boundaries

The current environment cannot connect directly to MangaDex to retrieve copyrighted image pages or complete the pilot. There is no verified full-series artefact in this repository. Be mindful of source copyrights and scanlation-group permissions; personal use does not authorise rehosting or distributing pages. The creator and scanlation groups must be credited where appropriate, and removal requests honoured. Do not commit page images, scans, CBZs, passwords or tokens, and do not publish them as public GitHub Actions artefacts. This is an opt-in **local** route, not an assertion that MangaDex grants permanent download rights. The exact API/reader availability and publisher policies can change.

The existing Controller candidate importer can be used **only if** the produced CBZs are compatible with the strict image-only archive contract. The current ReLIFE audit tolerates safe `ComicInfo.xml` metadata, which the generic Controller import does not, so do not claim automatic Reader/HF integration.
