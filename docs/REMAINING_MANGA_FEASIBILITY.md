# Remaining requested manga: source and offline-feasibility review

Research date: **20 November 2026**. Covers the six titles left after the ReLIFE, Maid-sama!, Last Game and Onizuka-chan batch work, plus the previously requested *Love So Life*. Every claim below separates **online catalogue visibility**, **English translation**, **actual media access**, and **permission to export/archive**. An online reader is not a verified full-quality CBZ download source.

## Findings

| Title | MangaDex evidence (19 Nov metadata job) | Other visible sources | Rights/download result | Decision |
| --- | --- | --- | --- | --- |
| **Kainushi wa Akuma** (Eiri Kaji) | 45 English entries; mostly decimal labels; sampled original-page manifest 34 paths. Numbering does not align cleanly with integer chapter ranges. | [OniSaga](https://onisaga.com/title/kainushi-wa-akuma) lists about 56 English chapter entries (includes subchapters). The site returned HTTP 403 when externally opened, so further access could not be verified. | No creator/publisher authorisation for unattended media retrieval or public-artefact redistribution established. | **Partial MangaDex candidate**; investigate chapter label mapping, editions, actual file quality, rights before any download job. |
| **Kimi no Iru Machi / A Town Where You Live** (Kouji Seo) | **0** English feed entries. | [Weeb Central](https://weebcentral.com/series/01J76XY7F049Y3WQ1WM57D8VGD/Kimi-No-Iru-Machi) lists the series and a [chapter 261](https://weebcentral.com/chapters/01J76XZ0KMM9VF7W2V2AX5HQ9Q); English official licensing not established. | Weeb Central's [FAQ](https://weebcentral.com/faq) explicitly says it will not provide a download option owing to server load. No permitted bulk/download contract confirmed. | **Readable alternative located; no suitable authorised automation source verified.** |
| **Love Hina** (Ken Akamatsu) | **2** English feed entries; sampled chapter manifest had **0** hosted original page paths. | [Kodansha's official *Love Hina Omnibus*](https://kodansha.us/series/love-hina-omnibus/) is complete, with **5 print/digital omnibuses** compiling the original 14-volume story. [Weeb Central](https://weebcentral.com/series/01J76XY7Z542X29BECZC50JKY1/Love-Hina) lists community reading chapters but not a download feature. | Official Kodansha products are paid digital reading/purchase options, not proven DRM-free CBZ exports. No automated archival authorisation confirmed. | **Use licensed omnibus for complete, publisher-quality English; MangaDex unsuitable for full download.** |
| **Lovely Complex / Love★Com** (Aya Nakahara) | Standard edition: 71 English records, **66/66** integer-numbered chapters, but sampled chapter 1 manifest **0** hosted images. Separate digital-colour listing: 0 English records. | [VIZ official English Love★Com](https://www.viz.com/love-com); 17 original manga volumes. The [*Lovely Complex Plus*](https://weebcentral.com/series/01J76XY7MEVEK56NZG7C9H37K0/Lovely-Complex-Plus) listing is **bonus material**, not the main series. | VIZ offers previews/purchases; neither VIZ nor MangaDex provides a verified complete downloadable CBZ edition here. | **Official English volumes exist; investigate publisher/offline formats, not MangaDex bulk images.** |
| **Mado kara Madoka-chan** (Yasuhiro Fukuda) | **0** English feed entries. | [Kodansha Japan](https://www.kodansha.co.jp/titles/1000029365) lists a **completed five-volume Japanese** edition. [Goda reader](https://manhuascans.org/manga/mado-kara-madoka-chan) exposes a chapter labelled **74.1 / afterword**, but calls it 'ongoing', inconsistent with the publisher's completed status. | External reader is not proof that every chapter is translated, intact or downloadable. No licence or automated media rights established. | **Possible community translation source, but metadata and rights uncertain; do not trigger public artwork retrieval.** |
| **Nisekoi: False Love** (Naoshi Komi) | Only **5** English entries; sampled original hosted image paths **0**. | [VIZ official English Shonen Jump chapter index](https://www.viz.com/shonenjump/chapters/nisekoi) lists **chapters 1–229**; [25 official volumes](https://www.viz.com/nisekoi-false-love) include the conclusion. [Weeb Central](https://weebcentral.com/series/01J76XY7F84AQF7DNFA0865TGQ/Nisekoi) also lists the work as complete. | Most official VIZ chapters require reading access. These publisher reader pages do not provide export rights or a documented DRM-free CBZ API. | **Complete, reliable official English reading available; MangaDex bulk unsuitable and automatic offline extraction unverified.** |
| **Love So Life** (Kaede Kouchi) | [Live MangaDex metadata check](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44590570263): **119 English feed entries; 106/106 contiguous numbered main chapters (1–106), 5 distinct decimal-numbered extras**, and 50 original-upload image paths in the sampled first chapter. Exact title ID: `911a12ae-1022-448e-9219-b7b294d7fb3e`. | [Weeb Central listing](https://weebcentral.com/series/01J76XY7HRJYFAPKGKPAN85H65/Love-So-Life) says 'Complete' and visibly shows chapter **106**; [AniList](https://anilist.co/manga/44236) and other catalogues index **111** chapters. [Hakusensha](https://www.hakusensha.co.jp/comicslist/46650/) publishes the 17th/final Japanese volume; no official English edition confirmed. | Reader chapter 106 versus catalogue 111 is a **coverage discrepancy**, not a verified missing-chapter result. Weeb Central has no authorised download feature. | **Promising full MangaDex English hosted-page candidate**, but mapping 106 numbered + 5 extras to the independent 111-chapter catalogue requires checking; no approved automated media distribution rights. |

## Engineering assessment and safe next steps

1. **Do not treat a reader listing as an automatically downloadable dataset.** For every target, verify exact edition/title, source chapter IDs and missing/extras; original versus compressed page dimensions; site-specific rights and an explicitly allowed download/export mechanism.
2. **Highest-priority next pilot candidate:** Love So Life (106 contiguous MangaDex numbered English chapters + five extras, 50 sample original-image paths). Verify exact 111-chapter catalogue mapping, source permissions and sample image fidelity first. Kainushi wa Akuma remains a follow-up for irregular fractional chapter numbering. For the remaining titles, catalogued English reading or official digital volumes do not translate to lawful GitHub artefact uploads.
3. **Official English-first choices:** Kodansha Love Hina Omnibus, VIZ Love★Com, and VIZ Nisekoi. Publisher masters are usually preferable for visual fidelity, but **no unprotected CBZ export** was demonstrated.
4. **Avoid an automated public-media run for these seven** until rights are independently confirmed. A public repo's GitHub Actions artefacts are publicly retrievable; private intentions do not change visibility. No DRM/login/paywall/anti-bot bypass.
5. After an authorised source is identified, test **a single chapter privately**, verify publisher/scanlator attribution, page count, dimensions and SHA-256, then consider bounded Actions automation.

## Evidence and limits

- Original eight-title [live MangaDex metadata audit](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44549436127) and [Lovely Complex edition comparison](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44550113059). These fetched metadata/page **manifests only**, not copyrighted image bytes.
- A web-visible chapter link or a catalogue claiming 'complete' does not prove that all chapters are actually accessible, English-translated or correctly ordered.
- External reading sources may change, block traffic, have limited rights, expose inconsistent chapter numbers or show missing content. Do not report full-series downloads without actual verified files and chapter inventories.

### Love So Life live check (19 November 2026)

The [Love So Life English MangaDex Metadata Probe](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44590570263) resolved the exact title `911a12ae-1022-448e-9219-b7b294d7fb3e` and found **119 English feed entries**, **106 distinct integer chapters without gaps 1–106**, **five decimal-numbered extras**, and **50 normal/original uploaded image paths** for the first numbered chapter. The total 119 feed entries includes alternate/duplicate releases; 106 + 5 = 111 distinct numbered/decimal labels **could account for the 111-chapter catalogue count**, but is not independent confirmation of the edition or completeness. No image bytes were downloaded.

## Follow-up: MangaKatana chapter metadata (20 November 2026)

A [five-title, metadata-only GitHub Actions check](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44679559853)
used the pinned third-party CLI's `list --json` subcommand with exact known MangaKatana series URLs. All five listings returned matching series titles and complete **expected main chapter numbering**: Kimi no Iru Machi 261/261, Love Hina 120/120, Lovely Complex 66/66, Mado kara Madoka-chan 74/74, Nisekoi 229/229. Eleven decimal and one chapter-zero Nisekoi extras were catalogued separately. See [full breakdown](FIVE_MANGA_CATALOGUE.md).

**Change in assessment:** The remaining five now have a technically promising **chapter-listing** route beyond MangaDex. This overturns the earlier *technical* assumption that there was no chapter inventory route, but **does not establish English page quality, permission to download, or authorised public GitHub Actions artefact redistribution**. No new CBZ jobs were triggered. Prior rights/download cautions remain in force.


## Follow-up: six NEW English manga acquisition check (21 November 2026)

This check is limited to **Kimi no Iru Machi, Love Hina, Lovely Complex, Mado kara Madoka-chan, Nisekoi, and The Fairytale-like You Goes on the Assault**. Completed historical titles are excluded.

### Newly verified official/export findings

| Target | Official English route found | Export/retention result |
| --- | --- | --- |
| **Kimi no Iru Machi** | The former English Crunchyroll Manga licence is documented historically, but the original Crunchyroll digital manga service closed on 11 December 2023. A current Crunchyroll anime page is not a manga edition, and no current English volume/export listing was verified. | No current authorised DRM-free English export. The 19 November MangaDex audit found 0 English entries. Weeb Central is a reader listing and explicitly does not offer downloads. |
| **Love Hina** | Kodansha's five-volume English Omnibus is listed by Kodansha, Omoi and GlobalComix. Omoi identifies Kodansha as publisher; GlobalComix's five release pages identify Kodansha. | **One conditional publisher-authorised file-export lead (DRM status unverified):** Kodansha's official 2020 Humble Bundle announcement included all five English Omnibus volumes and explicitly offered CBZ, PDF and ePub files. The sale ended 10 June 2020. The publisher announcement confirms downloadable CBZ, PDF and ePub formats, but does not explicitly state DRM status. Inspect the actual purchaser download page/file before treating it as DRM-free. This route is usable only if the owner already has a Humble purchase entitlement; account ownership was not checked and no files were accessed. Current Omoi volumes do not display the ePub-availability notice that Omoi says identifies DRM-free downloads. GlobalComix's Love Hina pages show Preview/Buy and Gold reading, not a PDF-download option; GlobalComix distinguishes DRM-free PDF Downloads from app-only Collection Unlocks. Kodansha Reader Portal also says its digital volumes are not offered as downloadable files. |
| **Lovely Complex / Love★Com** | VIZ's official English edition and volume catalogue are confirmed. | VIZ preview/retail reading is available, but no authorised DRM-free CBZ/PDF/EPUB export was verified. The 19 November MangaDex audit found 71 English feed records but 0 hosted original-page paths in the sampled chapter 1 manifest. |
| **Mado kara Madoka-chan** | Kodansha Japan lists the completed five-volume original edition. | No official English edition or authorised English export was found. The 19 November MangaDex audit found 0 English entries. |
| **Nisekoi: False Love** | VIZ lists the complete English series, 25 volumes and its chapter catalogue. | VIZ's web reader and retailer purchases are not a verified archival export. Kobo's English EPUB3 listing specifies Adobe DRM. The 19 November MangaDex audit found only 5 English feed entries and 0 hosted original-page paths in the sample. |
| **The Fairytale-like You Goes on the Assault** | The original is creator-posted Japanese work by Hazano Kazutake. | OniSaga currently lists 77 English community-translated chapters out of 78; this is not an official publisher edition or an export licence. No exact MangaDex title ID or authorised English export was verified. The existing MangaKatana first-chapter pilot's 8 pages still have unverified language and rights. |

The Love Hina Humble Bundle is the only newly verified English publisher-announced downloadable-file route among these six; **DRM status and owner entitlement remain unverified**. It is conditional on an existing purchase rather than a currently purchasable offer. Manga Library Z historically distributed all 14 original Japanese Love Hina volumes as author-authorised PDFs, but this is no longer a live acquisition route. Its operator's official closure notice states that the internet distribution service was stopped and gives 26 November 2024 as the planned shutdown date. The historical Japanese edition does not satisfy the English requirement.

### Technical source evidence and retained outputs

- The six-title MangaKatana first-chapter evidence is unchanged: the first five pilots reported 246 verified image pages combined; the Fairytale pilot reported 8. Those files were ephemeral, removed from public runners, and are not retained deliveries. English text and archive rights remain unverified.
- MangaDex results remain the 19 November metadata audit already recorded above. No identical MangaDex or ManhuaTop probes were repeated because no meaningful upstream change was identified.
- Upstream [Manga Downloader v25.3.0](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0) advertises support for 584 sites, including MangaDex. That is a technical domain list, not proof of a working image fetch for these titles or permission to archive their artwork. No new aggregator image tests were run without an authorised export basis.
- PR #39 remains the latest merged PR and main remains at `47ab56f`; no newer PR was found.
- ManhuaTop run [44803983855](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44803983855) still has four failed metadata diagnostics only: artefacts `14662650937` (490 bytes), `14661628427` (566 bytes), `14660409466` (519 bytes), and `14659944929` (559 bytes), expiring 27 November 2026.
- Fairytale run [44789220759](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44789220759) retains report artefact `14655881240` (804 bytes), expiring 27 November 2026; it does not contain the eight pilot images.
- CI run [44804426050](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44804426050) passed Windows, Linux and security jobs. It produced no media artefacts.

### Decision and exact blockers

No new source met all four gates: English page content, complete chapter/volume coverage, verified original-page integrity, and an explicit lawful export/retention permission. Consequently no source adapter or image-download test was added, no media batch was launched, and no new title is claimed as downloaded.

The next actionable path is **Love Hina only if the owner already purchased the 2020 Kodansha Humble Bundle**: download the five English Omnibus files from that existing account entitlement onto the owner's Windows machine, then run the Retriever's local import and verification workflow. The automation cannot inspect the owner's Humble account, operate the owner's Windows machine, or access an approved private runner. Public GitHub Actions and private Hugging Face are not acceptable destinations for unlicensed manga pages. If there is no existing Humble entitlement, the remaining blocker is title-specific rights-holder permission or a newly offered English DRM-free edition.

Manga Storage Controller and Manga Library were not modified.


## Follow-up: creator-rights and alternative-source audit (22 November 2026)

This check did not authorise any new image retrieval. It records newly surfaced reader indexes and upstream changes so that technical availability is not mistaken for export permission.

### Newly surfaced non-authorised reader indexes

- [OniSaga's A Town Where You Live index](https://onisaga.com/title/a-town-where-you-live) advertises 293 English chapter records.
- [OniSaga's Love Hina index](https://onisaga.com/title/love-hina) advertises 144 English records; the page itself says coverage is unknown and includes fractional/extra labels.
- [OniSaga's Love★Com index](https://onisaga.com/manga/love-com) advertises 100 English records, including split chapters and extras; this is not a verified 66-chapter main-series mapping.
- [OniSaga's Fairytale index](https://onisaga.com/title/hakanai-kimi-wa-moukou-wo-hajimeru) advertises 77 English chapters out of 78.
- Search-indexed OniSaga pages also expose English-labelled Nisekoi chapter pages, but a reliable complete English inventory was not established. No Mado kara Madoka-chan English index was verified.

These are community-reader/catalogue observations only. Direct page opening for the OniSaga title pages returned HTTP 403 during this check, so reader image access and chapter integrity were not independently tested. No 403, browser challenge or access restriction was bypassed. No image requests or downloads were made.

### Fairytale creator's explicit reuse restriction

Hazano Kazutake's public creator profile for **@TEIGI_3** states that reposting is prohibited. The creator's indexed Pixiv profile text further says the work is posted only on the creator's Pixiv, X, Bluesky and personal homepage, and asks that translations not be posted on overseas sites. See the creator-profile index [here](https://sakuria.syarolia.com/artworks/131219914) and the creator's [X profile](https://x.com/TEIGI_3). The profile restriction is incompatible with treating third-party English reader uploads as an authorised export. **Do not download or archive the community English chapters unless the creator supplies explicit written permission or an authorised English edition.**

### Upstream downloader change review

Upstream [Manga Downloader v25.3.0](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0), released 18 November 2026, advertises 584 supported sites and adds chikari.moe, manhuaplus.top and manhuaplus.org, alongside volume handling and fixes. These additions are not publisher/creator export grants and none was established as an authorised source for the six targets. The release notes do not report a ManhuaTop fix; the four failed ManhuaTop probes from run 44803983855 therefore remain closed and were not repeated.

### Official publisher position rechecked

- Kodansha's official [2020 Humble Bundle announcement](https://kodansha.us/2020/05/20/get-over-1500-worth-of-award-winning-manga-for-20-with-this-humble-manga-bundle-ends-69/) confirms all five English Love Hina Omnibus volumes were included and that the bundle supplied CBZ, PDF and ePub formats. The offer ended 10 June 2020; the announcement does not state DRM status. Existing purchaser entitlement and the actual download-file restrictions remain unverified.
- [Omoi's Love Hina page](https://www.omoi.com/series/love-hina) shows licensed volume purchases. Omoi's [FAQ](https://www.omoi.com/faq) says app offline reading is not the same as export; DRM-free volume files are only available where the volume page explicitly advertises ePub availability. No such notice was found for Love Hina.
- Kodansha's [Support Center](https://kodansha.us/support-center/) says Reader Portal digital content is website-only and is not offered in downloadable formats.
- VIZ continues to list official English digital volumes for [Love★Com](https://www.viz.com/love-com) and [Nisekoi](https://www.viz.com/nisekoi-false-love), but its reader/retailer listings do not establish a portable CBZ/PDF/EPUB export right.
- No current official English edition or permitted English export was found for Kimi no Iru Machi, Mado kara Madoka-chan or The Fairytale-like You Goes on the Assault.

### Decision

No newly discovered source passed the required gates of explicit rights, English page content, complete chapter coverage, original-page integrity and a lawful portable retention route. No source adapter, image test, download batch or media artefact was created. Existing MangaDex, MangaKatana and ManhuaTop evidence remains unchanged. The conditional Love Hina Humble entitlement remains the only plausible publisher-announced portable-file route, pending proof that the owner purchased it and inspection of the actual download terms/files.

For the exact retained report artefact IDs, expiry timestamps, per-title sample ranges, image-page counts, CBZ byte counts and all 35 temporary-archive SHA-256 receipts from the follow-up audit, see [the 22 November new-manga pilot evidence ledger](NEW_MANGA_PILOT_EVIDENCE_20261122.md).


## Follow-up: Love Hina legacy J-Comi / Manga Library Z route status (22 November 2026)

A further check resolved an ambiguity in the earlier Love Hina research:

- The original J-Comi service did distribute all 14 Japanese *Love Hina* volumes as free PDF files in its November 2010 beta. The contemporaneous Japanese technology report records high- and low-resolution PDF downloads. This was a historical, creator-led release, not an English edition. See [INTERNET Watch's 26 November 2010 report](https://internet.watch.impress.co.jp/docs/news/409632.html).
- Manga Library Z's operator later published an [official service-closure notice](https://closing.mangaz.com/). It says the internet e-book distribution service would stop and identifies 26 November 2024 at 12:00 as the planned stop time. Its [5 November 2024 payment notice](https://closing.mangaz.com/info/2113/index.html) records the end of premium registration and changes to PDF-purchase payment methods.
- Therefore, Manga Library Z/J-Comi is **historical evidence of an author-authorised Japanese PDF distribution**, not a currently usable download source. Do not treat old URLs, search results, mirrors or cached listings as a current export route.
- This does not change the conditional English route: the 2020 Kodansha Humble Bundle remains the only publisher-announced English CBZ/PDF/ePub lead found for Love Hina. The offer ended 10 June 2020; the owner's entitlement and the actual file's DRM/terms remain unverified.
- No file was downloaded, no account was accessed, and no media retrieval was attempted.

The upstream Manga Downloader review remains unchanged: v25.3.0 is the latest checked release (18 November 2026), with 584 supported sites. Its new site additions do not identify an authorised source for any of the six targets. The failed ManhuaTop run 44803983855 remains closed; no identical probe was repeated.


## Follow-up: supported alternative readers and retention recheck (22 November 2026)

### New technical alternatives, not authorised export sources

The latest upstream [Manga Downloader v25.3.0](https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0), released 18 November 2026, remains the newest release checked and advertises 584 supported sites. Its source at commit [b7c87ef](https://github.com/elboletaire/manga-downloader/tree/b7c87ef24a8c7a96574fb0c6862858ca00356800) contains dedicated MangaDex, WeebCentral and MangaFire grabbers, as well as MangaKatana support. Its `list --json` command can inspect chapter metadata, languages and groups without downloading pages. These integrations establish technical client support only, not image retrieval for a particular title or archival permission.

Newly surfaced exact-title indexes:

- [WeebCentral: Kimi no Iru Machi](https://weebcentral.com/series/01J76XY7F049Y3WQ1WM57D8VGD/Kimi-No-Iru-Machi) marks the series complete, lists chapters 1–261 and explicitly says **Official Translation: No**. This is a community-reader listing, not an authorised export.
- [WeebCentral: Love Hina](https://weebcentral.com/series/01J76XY7Z542X29BECZC50JKY1/Love-Hina) marks the series complete and **Official Translation: Yes**, with fractional labels including 118.5–118.8. That field describes the translation, not the site's right to distribute page images or our right to archive them. No portable export permission is stated.
- MangaFire's indexed [Love Hina](https://mangafire.to/title/20w5-love-hinaa), [Lovely Complex](https://mangafire.to/title/6wrz-lovelycomplex) and [Nisekoi](https://mangafire.to/title/l326-nisekoi-false-love) pages are labelled English. Its indexed Lovely Complex listing identifies chapter 66 as the final chapter; Love Hina surfaces chapters 123 and 124. These are reader-index observations, not verified full inventories or publisher exports. Direct page opens returned no readable lines, so no image retrieval or completeness test was performed.
- No English Mado kara Madoka-chan listing was found in these checks. The Fairytale creator restriction recorded above still rules out treating third-party English reader uploads as authorised.

No image tests were run against MangaDex, WeebCentral or MangaFire. The source material surfaced through community-reader listings, and no rights grant or authorised portable export was established. No CAPTCHA, login, paywall or browser challenge was accessed or bypassed. The existing MangaDex metadata audit remains the only title-specific MangaDex evidence in this repository.

### GlobalComix export distinction rechecked

GlobalComix's [official FAQ](https://globalcomix.com/support/faq) distinguishes DRM-free PDF Downloads, which provide a permanent downloadable file, from Collection Unlocks, which grant a reading licence; offline reading of Collection Unlocks requires GlobalComix Gold. The current [Love Hina Omnibus 5 release page](https://globalcomix.com/c/love-hina-omnibus/r/4e3b7e1e-67ee-4a13-8a17-ad25b93efcb7) exposes Preview and Buy ($14.99), not a Buy PDF option. The current GlobalComix listing therefore does **not** establish a DRM-free Love Hina export. No purchase or file download was attempted.

Kodansha's [official Love Hina Omnibus series page](https://kodansha.us/series/love-hina-omnibus/) currently lists all five digital volumes, but does not expose a portable file export. The historical [2020 Kodansha Humble Bundle announcement](https://kodansha.us/2020/05/20/get-over-1500-worth-of-award-winning-manga-for-20-with-this-humble-manga-bundle-ends-69/) remains the only publisher-announced English CBZ/PDF/ePub route found. The sale ended 10 June 2020; the owner's purchase entitlement and actual file DRM/terms remain unknown. The Gmail entitlement search could not run in this non-interactive check because the connector required user input.

### Actions and retained-output spot check

Repository state at this check:

- Main: `0710898b2679a885a4d66283f91251ae66385cd8`.
- Latest PR: [#44](https://github.com/RichardDaffern/Manga-Retriever/pull/44); open PR count: 0.
- Latest main CI [44947163318](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44947163318) and PR CI [44947010247](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44947010247) both passed and produced no artefacts.

The retained acquisition artefacts remain reports, not manga files:

- First-chapter run [44755633296](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44755633296): five JSON receipts, IDs `14638010391`, `14636799475`, `14638046053`, `14639050165`, `14638515660`; each expires 23 November 2026 between 14:41 and 14:43 UTC.
- Early/middle/final coverage run [44783810968](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44783810968): 15 JSON receipts, IDs and individual SHA-256 values are recorded in [the evidence ledger](NEW_MANGA_PILOT_EVIDENCE_20261122.md); they expire 27 November 2026 between 17:30 and 17:38 UTC.
- Fairytale run [44789220759](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44789220759): artefact `14655881240` (804 bytes), expiring 27 November 2026 18:04:13 UTC.
- ManhuaTop run [44803983855](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44803983855): diagnostic artefacts `14662650937`, `14661628427`, `14660409466`, `14659944929`; all expire 27 November 2026 around 19:38 UTC. These four failed probes were not repeated.

Downloaded and inspected three retained ZIPs: `14655881240`, `14651384279` and `14638010391`. They contain JSON reports only. The Fairytale receipt reports one temporary CBZ and eight decoded pages, but `userOwnedFilesRetained=false` and `rightsToPublishMediaIndependentlyVerified=false`. The two Kimi receipts report temporary chapter files with 60 and 43 pages respectively, no explicit English source label, manual language review required, and `publicCIArtifactPermitted=false`. The CBZ bytes were not in the ZIPs and are not retained. No persistent destination or retained media hashes exist.

### Decision

No new source passed the required rights, English-language, completeness, integrity and lawful-retention gates. No source adapter, image test or media batch was launched. The 35 previously verified temporary MangaKatana CBZs and 1,032 pages remain ephemeral evidence only; their 35 SHA-256 receipts are documented in the evidence ledger. No new title or chapter is claimed as retained.

Exact blockers remain: no title-specific archival permission for the reader sources; unknown Humble Bundle entitlement and file terms for Love Hina; no owner-controlled Windows execution in this environment; and no approved private runner or persistent destination. The minimal route is an owner-controlled Windows staging folder or secure self-hosted runner, plus a verified licensed file/export for the selected title. Do not use public Actions artefacts or Hugging Face for these manga pages.
