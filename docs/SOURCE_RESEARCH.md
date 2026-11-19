# Manga source research and redistribution checks

**Research update: 19 November 2026.** Free online reading, an API or access through a browser does not imply permission to copy chapters. Treat per-work terms and archival/download permissions as separate questions.

## Strong candidate for actual Japanese manga

**Give My Regards to Black Jack / ブラックジャックによろしく, by SHUHO SATO (佐藤秀峰).** The author announced in June 2024 that he made a higher-quality *Complete Edition* consisting of 13 volumes and cover illustrations available at https://densho810.com/free/ as DRM-free PDFs. The owner's original site publishes the full bilingual secondary-use terms: https://densho810.com/free/ . The author's announcement: https://note.com/shuho_sato/n/n4a30c9db7916?hl=en . An independent university guide identifies both Japanese and English downloads: https://guides.lib.ku.edu/c.php?g=94978&p=7378433 .

**Important conditions**: explicitly credit the title and author in the stipulated language (English: `Give My Regards to Black Jack`, `SHUHO SATO`); use only Sato Manga Works' own supplied PDFs, not scans of other book editions; the sequel is excluded. No unauthorised Amazon Kindle use; on e-book distribution stores the work must be priced at least one yen. Secondary-use publication has a post-publication reporting requirement by email within one month, plus third-party music-rights caveats on specified pages. These are not merely CC BY terms. Confirm the currently published terms before release or republication.

**Decision:** High-priority actual-manga source candidate. Official PDF links, file sizes, safe rate limits and PDF-to-CBZ fidelity must be verified before enabling automatic download and redistribution through a public Actions artefact. The M6 GitHub artefact retriever currently does *not* support this source. **Local official-PDF import is now implemented** with explicit owner provenance declaration, original PDF SHA-256, PNG rasterisation, exact volume count option and per-image CBZ integrity validation. See [PDF importer guide](BLACKJACK_PDF_IMPORT.md). A remote adaptor remains pending direct download link and public-artifact terms validation.

## Other researched candidates

| Source | Current rights evidence | Implementation policy |
| --- | --- | --- |
| Pepper&Carrot | Creator's CC BY 4.0 source pages, including https://www.peppercarrot.com/en/webcomic-sources/ep26_Books-Are-Great.html | ep26 enabled. Episode 25 also has creator-published downloadable hi-res English pages and episode-specific credits: https://www.peppercarrot.com/en/webcomic-sources/ep25_There-are-no-Shortcuts.html . Additional episodes need their own bounded URL/page/credit plan before activation. |
| Wikimedia Commons | https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/en | Item-by-item licence checks and attribution; no generic manga series archive. |
| National Diet Library | https://www.ndl.go.jp/en/use/reproduction | Confirm per-item public-domain status before retrieval. |
| MangaDex | https://api.mangadex.org/docs/ | Metadata research only. An API does not grant permanent image archiving rights. |
| Manga Plus / Kodansha and other official readers | https://kodansha.us/support-center/ ; publisher free previews are read-only | No general download adapter. Kodansha explicitly states digital books are not offered as downloads. |
| ComicFury | https://comicfury.com/tos.php | No general archival adapter without specific creator/platform permission. |

Next stage: validate PDF provenance, establish exact downloadable links and preservation rules, then add regression-tested adapters without enabling arbitrary site scraping or bypassing paywalls, DRM, authentication or anti-bot controls.

## Follow-up: user's remaining named manga

For a title-by-title comparison of additional English sources, publisher editions, reader coverage, image/export feasibility and blockers, see [Remaining manga source feasibility](REMAINING_MANGA_FEASIBILITY.md) (researched 20 November 2026). No downloads from these seven titles were triggered by that research.
