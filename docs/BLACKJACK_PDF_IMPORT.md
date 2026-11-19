# Creator-authorised Japanese manga: Give My Regards to Black Jack

The creator **SHUHO SATO** makes the 13 volumes of **Give My Regards to Black Jack / ブラックジャックによろしく** available as downloadable DRM-free PDFs at https://densho810.com/free/ . The author confirmed the higher-quality Complete Edition in 2024: https://note.com/shuho_sato/n/n4a30c9db7916?hl=en .

## Rights and limitations

These are **creator-specific secondary-use terms**, not a Creative Commons licence. Read the latest terms on the official site before reusing or publishing: every product must visibly credit `Give My Regards to Black Jack` and `SHUHO SATO` (Japanese versions use the required Japanese wording); only the creator/publisher-provided data is covered, not scans of paper books; the sequel is excluded; Amazon Kindle and ebook-store distribution carry restrictions; and **public reuse must be reported to Sato Manga Works within one month**. Several original volumes also have third-party music-rights caveats. No general online manga site permission follows from this exception.

**Download the official PDFs manually** from the creator's page. This project does not yet automate their remote retrieval because direct links and downloadable file formats need independent verification. Keep the original PDFs privately as an archival backup.

## Windows conversion

Install Python 3.12 with PDF rendering support:

```powershell
py -3.12 -m pip install -e ".[pdf]"
```

Place the official PDFs in a dedicated folder containing **only** PDF files. Name them to ensure correct natural sorting by volume, such as `01.pdf`, `02.pdf`, ..., `13.pdf`. The tool will not guess from the actual names or check authenticity, so verify that the files came from Sato Manga Works yourself. Then run:

```powershell
py -3.12 -m manga_retriever.blackjack_pdf --source "C:\Manga\Official-PDFs" --output "C:\MangaExport\BlackJack" --registry "C:\MangaExport\ids.json" --expected-volumes 13 --scale 2.0 --official-source
```

Or supply exactly those arguments to `Import-BlackJack-PDFs.cmd`. For a partial set, omit `--expected-volumes 13` or use the actual count (1 to 13). Do not later combine partial sets using the same chapter registry without planning stable volume mappings.

The tool converts PDF pages into **new PNG raster images** before creating one verified CBZ per volume, plus a local `controller_candidate/`. It does **not** preserve the original PDF page-image encodings; instead `download_manifest.json` records the SHA-256 of each unmodified input PDF, the raster scale, per-volume page counts and the explicit declaration that publisher authenticity was not independently verified. It writes a SourceRights v1 declaration with the required credits; this does not fulfil any separate downstream publication reporting obligations. It never overwrites an output folder, uploads images or modifies the original PDFs.

**Quality:** Use scale `2.0` by default, or `2.5` for finer rendering if storage permits. PDF renderings are capped to control memory and decompression risks; large volumes may require importing smaller sets. A complete 13-volume ZIP is not yet automatically fetched from the website.
