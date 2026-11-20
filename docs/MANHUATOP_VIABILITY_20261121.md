# ManhuaTop viability audit: four NEW manga (21 November 2026)

**Website:** https://manhuatop.org/  
**Technical test:** [ManhuaTop four-title GitHub Actions run 44803983855](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44803983855)  
**Code:** [scripts/manhuatop_source_probe.py](../scripts/manhuatop_source_probe.py)  
**Policy:** [AGENTS.md](../AGENTS.md) and [SUPPORTED_SOURCES.md](SUPPORTED_SOURCES.md)

## Outcome

**Not viable for automated new-title chapter downloading on the current public GitHub Actions runner.** All four separate live attempts to read source chapter metadata through pinned `elboletaire/manga-downloader v25.3.0` failed (client exit 1), before a single manga image was fetched. The client reported browser/Chromium/network-related problems; one diagnostic additionally included HTTP 403. No successful real image/CBZ download was established. The website remains viewable in an ordinary web/browser context, but browser visibility alone is not a downloadable media pipeline.

The [upstream Manga Downloader v25.2.0 release notes](https://github.com/elboletaire/manga-downloader/releases/tag/v25.2.0) say ManhuaTop's redesigned site was fixed; that is a **compatibility claim for upstream, not proof it still works in our headless runner or on all current chapters**. The current public site loads its chapter list dynamically, and a non-JavaScript HTML response can show zero rendered chapter rows even when the page advertises a chapter count.

## Exact NEW source candidates tested

These four were never among the previously completed title download list.

| Title | ManhuaTop page | Live pinned-client result |
| --- | --- | --- |
| The Heavenly Demon Can't Live a Normal Life | https://manhuatop.org/manhua/the-heavenly-demon-cant-live-a-normal-life-mh/ | Failure: browser/Chromium/network category |
| Disastrous Necromancer | https://manhuatop.org/manhua/disastrous-necromancer-top/ | Failure: browser/Chromium/network category |
| High-Martial World: One Hand to Overwhelm Three Thousand Emperors! | https://manhuatop.org/manhua/high-martial-world-one-hand-to-overwhelm-three-thousand-emperors/ | Failure: HTTP 403 plus browser/Chromium/network category |
| Magic Emperor | https://manhuatop.org/manhua/magic-emperor/ | Failure: browser/Chromium/network category |

Source pages are **catalogue listings only** for purposes of this audit: they do not prove full English coverage, original-image fidelity, availability of chapter bytes for export or a copyright licence.

## Copyright and operational guardrail

The site's own [DMCA notice](https://manhuatop.org/digital-millennium-copyright-act/) describes copyright-protected material and user-submitted fragments. It does **not** grant a general licence to mass-download or distribute full series. A third-party downloader advertising domain support similarly does not confer rights to copy/re-host artwork. Therefore:

- **No copyrighted chapter files were downloaded, published as public artefacts or passed to private Hugging Face.**
- This new verification workflow reads **chapter metadata only** and uploads JSON diagnostic receipts, not media.
- No bypass of HTTP 403, browser security checks, CAPTCHA, paywalls or source access controls is permitted.
- Do **not** register ManhuaTop as a production-compatible download site or claim any title was acquired.
- Further debugging is appropriate only through non-bypass methods: ordinary published documentation/source contracts, clear publisher/source export permission, and non-circumventing network diagnostics with the upstream maintainers.

## Suggested next engineering direction

1. Retain read-only exact-source probes in code for future compatibility regressions and upstream issue reports, but **do not schedule noisy repeat attempts** while the site is unchanged.
2. For **new manga acquisitions**, prioritise properly licensed, exportable English editions or sources with an explicit download contract and an actual private owner-controlled destination.
3. Verify a **real complete page-containing CBZ** from a permitted sample source in an isolated environment, then validate full chapter coverage, English text, byte integrity, and private retention before promoting that source to `SUPPORTED_SOURCES.md` as usable.
4. Do not fall back to already downloaded ReLIFE, Love So Life, Maid-sama!, Last Game, Onizuka, or Kainushi as substitutes for new manga.

**Status summary:** Four attempted source checks, **zero successful listings**, **zero pages downloaded**, **zero new manga archives**. This is a closed negative result, not a background download in progress.
