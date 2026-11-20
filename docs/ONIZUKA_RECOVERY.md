# Onizuka-chan and Sawarida-kun: bounded recovery

Previous English chapter downloads for 1–49 (run [44587087000](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44587087000)) retrieved chapter images but failed the post-download completeness checker on an unexpected **Ch. 0 Oneshot.cbz**. The client also reported occasional 522 and network errors. The existing code correctly rejected chapters outside the intended range, but incorrectly classified chapter zero as an ordinary positive main chapter.

**Correction:** A structurally valid chapter-zero oneshot is audited page-by-page, hashed and included as a named extra, not counted as a main numbered chapter. Exact expected chapters must still all be present. Duplicated positive main chapters, unexpected positive chapters and missing positives continue to fail the job; only chapter 0 is newly recognised as an extra.

A new [Onizuka-only workflow](../.github/workflows/onizuka-recovery-download.yml) automatically starts three independent English, uploader-original chapter batches (1–20, 21–40 and 41–49), maximum two concurrently. Jobs export seven-day verified CBZ artefacts. The existing [Three Manga Batch Recovery](../.github/workflows/three-manga-recovery.yml) retries failed jobs at most twice after the new workflow completes.

**Do not misinterpret this as completed until all three new chapter-range jobs have passed.** Source originals are scanlator uploader files, not publisher masters; publicly accessible GitHub Actions artefacts do not constitute permission to redistribute them.
