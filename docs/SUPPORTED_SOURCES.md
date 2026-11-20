# Supported source and input matrix

**Status:** 20 November 2026. This is an **implementation and evidence matrix**, not a claim that every listed website grants download or redistribution rights. Read the [full project handbook](PROJECT_HANDBOOK.md) and [agent policy](../AGENTS.md) for trust boundaries.

| Input/site | Implementation | Actual media verification | Limitations |
| --- | --- | --- | --- |
| **Owner's folder of JPEG/PNG/WebP/AVIF images, ZIP or CBZ** | Local importer and verifier implemented | Synthetic Windows/Linux tests and full image/CBZ checks | Requires authorised source files; input ZIP and output path safety checks |
| **Pepper&Carrot official Episode 26** | Fixed English, CC BY 4.0 licensed adaptor, page checkpoints, CBZ/ZIP/EPUB, approved Actions | Real six-image high-resolution licensed export and original SHA-256 validation | **Only Episode 26** is in the approved public bulk media-source allowlist; required attribution |
| **MangaKatana** | Five pinned exact title URLs supported by local CLI, plus bounded two-worker parallel, resumable batches | [Five real Chapter 1 CBZs](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44755633296) totalled **246 verified images** | English page text needs review; remaining chapters and rights unverified; public CI deletes copyrighted files and retains **only JSON verification** |
| **MangaDex** | Read-only source and language feed probes; some local-only fixed-title wrappers (ReLIFE, selected works) | Historic fixed-title workflows; source manifest availability varies by chapter | Metadata-only feed entries often lead to **zero** hosted page paths; no generic public-authorised image archive source |
| **Owner-supplied English fixed-layout image EPUB** | DRM-free EPUB importer implemented | Live six-image creator-licensed EPUB-to-CBZ sample verified | No encrypted/DRM, remote image, Japanese or mixed/unknown language support; no arbitrary ecommerce downloads |
| **Creator-provided *Give My Regards to Black Jack* official PDF** | Offline PDF-to-PNG/CBZ converter implemented | Synthetic PDF regression tests | Must obtain official PDFs separately; creator terms are work-specific; Japanese original is not an English library edition |
| **Comizy** | Not integrated | Listing/reader page researched; direct image retrieval not successfully verified | No general adapter or permission evidence |
| **Weeb Central** | Not integrated | Reader/index research only | No verified approved portable export |
| **Tapas** | Not integrated for export | Official reader and in-app offline option researched | App-only offline, not an independently exportable CBZ source |
| **Other publisher/reader sites** | Research only | Title, purchase or app listing evidence | Must separately verify edition-specific DRM-free portable files and authorisation |

## Explicit supported title URLs: local MangaKatana pilot

The local URL downloader accepts exactly the following titles, **not arbitrary MangaKatana or arbitrary website URLs**:

- `https://mangakatana.com/manga/kimi-no-iru-machi.2162`
- `https://mangakatana.com/manga/love-hina.4545`
- `https://mangakatana.com/manga/lovely-complex.6103`
- `https://mangakatana.com/manga/mado-kara-madoka-chan.21642`
- `https://mangakatana.com/manga/nisekoi.553`

For local Windows usage, title-specific flags, resume and status reports, see [LOCAL_URL_MANGA_DOWNLOAD.md](LOCAL_URL_MANGA_DOWNLOAD.md). Source permission acknowledgement is not an independent copyright clearance; **never** upload unlicensed media to public GitHub Actions.

## Highest-priority owner-selected source

**Acquainted: Encounter Spin-Off**: [MangaDex title UUID](https://mangadex.org/title/90f7c7a6-b759-4afb-b1cb-1af4660df307). Original work language Korean, but [exact MangaDex source audit](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44761569133) found **0 hosted chapters across every language/content rating**. The official English Tapas edition is readable in-app; an authorised portable file source has not been demonstrated. **No download should be claimed or attempted from that empty MangaDex feed.** See [priority report](PRIORITY_ACQUAINTED_ENCOUNTER_SPIN_OFF.md).

## Interpret success correctly

- **Catalogue listing**: the title/chapter numbers may exist; no page bytes necessarily exist.
- **Original image manifest**: a source reported paths, but a page has not necessarily downloaded.
- **Technical image pilot**: actual page bytes passed validation temporarily, but language/rights/full coverage and permanent storage may remain unverified.
- **Verified retained export**: complete intended chapters exist in an authorised private local folder or explicitly permitted licence-approved artefact, with page counts and checksums.
- **Controller accepted/uploaded**: this separate step requires the Controller's actual validator and an owner-approved operation.

The public media allowlist remains `peppercarrot:26`; this is **different** from local fixed URL technical pilots and metadata research. If a future source is added, document its exact work/host allowlist, licence, page/volume/chapter coverage, rate limits, output contract, tests and rights status here.

Additional context: [source research](SOURCE_RESEARCH.md), [remaining works feasibility](REMAINING_MANGA_FEASIBILITY.md), [download guide](DOWNLOAD_GUIDE.md), [architecture](ARCHITECTURE.md).
