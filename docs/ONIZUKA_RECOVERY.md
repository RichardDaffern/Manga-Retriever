# Onizuka-chan and Sawarida-kun: bounded recovery

Previous English chapter downloads for 1–49 (run [44587087000](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44587087000)) retrieved chapter images but failed the post-download completeness checker on an unexpected **Ch. 0 Oneshot.cbz**. The client also reported occasional 522 and network errors. The existing code correctly rejected chapters outside the intended range, but incorrectly classified chapter zero as an ordinary positive main chapter.

**Correction:** A structurally valid chapter-zero oneshot is audited page-by-page, hashed and included as a named extra, not counted as a main numbered chapter. Exact expected chapters must still all be present. Duplicated positive main chapters, unexpected positive chapters and missing positives continue to fail the job; only chapter 0 is newly recognised as an extra.

A new [Onizuka-only workflow](../.github/workflows/onizuka-recovery-download.yml) automatically starts three independent English, uploader-original chapter batches (1–20, 21–40 and 41–49), maximum two concurrently. Jobs export seven-day verified CBZ artefacts. The existing [Three Manga Batch Recovery](../.github/workflows/three-manga-recovery.yml) retries failed jobs at most twice after the new workflow completes.

**Verified complete for the requested numbered chapters on 20 November 2026:** [run 44675324997](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44675324997), attempt 2, finished successfully. Every range passed independent CBZ page checks and produced an unexpired artefact at the time of verification:

| Range | Main chapters verified | Pages checked | Artefact ID | Expires (UTC) |
| --- | ---: | ---: | --- | --- |
| 1–20 | 20 | 103 | 14601682680 | 27 November, 04:39 |
| 21–40 | 20 | 124 | 14602302471 | 27 November, 04:40 |
| 41–49 | 9 | 47 | 14602338397 | 27 November, 04:46 |

Total: **49/49 requested numbered chapters, 274 decoded image pages**. This does not assert every optional decimal extra is complete. The public artefact links are short-lived.

 Source originals are scanlator uploader files, not publisher masters; publicly accessible GitHub Actions artefacts do not constitute permission to redistribute them.
