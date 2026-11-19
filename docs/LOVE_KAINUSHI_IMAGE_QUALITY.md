# Love So Life / Kainushi wa Akuma: bounded image-quality pilot

The [ephemeral image-quality Actions workflow](../.github/workflows/love-kainushi-image-quality.yml) takes at most **two English chapters per exact title** and at most **one page per chapter** in each of the MangaDex *original-uploaded* and *data-saver* modes.

The comparison uses the official MangaDex@Home image server response. For each sample it checks JPEG/PNG/WebP decoding, width, height, byte count, image format, pixel count and SHA-256 in volatile job memory only. Source image bytes are **not committed, cached, saved or uploaded** as GitHub Actions artefacts; the output contains metrics and hashes only.

- HTTPS @Home hosts are restricted to MangaDex DNS names, redirecting is disabled, filenames and page hashes are validated, and per-page network and decoded pixel quotas apply.
- A quality comparison only tells us whether *MangaDex's uploader-original image* has more pixels or storage bytes than its data-saver version. It **cannot establish identity with a publisher's originals** or a scanlator's quality claims.
- Work remains subject to the API [acceptable-use policy](https://gitlab.com/mangadex-pub/mangadex-api-docs/-/blob/main/index.md) and copyright holders. The workflow never assumes that browsing or temporary decoding establishes permission to retain or redistribute full chapters.
- The offline inventory findings in [LOVE_KAINUSHI_READINESS.md](LOVE_KAINUSHI_READINESS.md) remain independently valid. No automatically redistributable full-title CBZ packages are enabled here.

The output artefact is **metrics only** and expires after seven days. A failed sample must remain clearly marked and cannot be called quality-verified.

## Live image-decoding results, 20 November 2026

The [successful GitHub Actions quality run](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44595345841) fetched, decoded, checked, discarded and reported metadata for four pairs of **one-page** image samples. All **4 of 4** chapter samples passed (original-upload + data-saver, eight temporary image responses total).

| Title / sample label | Original-uploaded image | Data-saver image | Pixel dimensions identical? |
| --- | --- | --- | --- |
| Love So Life ch. 1, page 1 | PNG, 850 × 1357, **1,252,748 bytes** | JPEG, 850 × 1357, **90,106 bytes** | Yes |
| Love So Life ch. 106, page 1 | JPEG, 482 × 510, **245,181 bytes** | JPEG, 482 × 510, **35,379 bytes** | Yes |
| Kainushi wa Akuma ch. 1, page 1 | PNG, 730 × 674, **556,531 bytes** | JPEG, 730 × 674, **42,189 bytes** | Yes |
| Kainushi wa Akuma ch. 25.5, page 1 | PNG, 720 × 1072, **251,835 bytes** | JPEG, 720 × 1072, **72,085 bytes** | Yes |

The original-uploaded files were larger, usually lossless PNG rather than the compressed data-saver JPEG. However, **both modes had the same dimensions** for all four samples. A first page may be a cover, credits or notes and is not a representative full-chapter clarity benchmark. No source-publisher masters were retrieved for comparison. Do not claim that the official publisher's full-resolution art was obtained.

The [metrics-only artefact](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44595345841/artifacts/14565227339) stores dimensions, byte counts, formats and SHA-256 only. The sample image bytes were held only in transient runner memory and were never published. Retention is seven days.

**Decision:** When retrieval is authorised, request MangaDex **original-uploaded** (data) rather than data-saver images for preservation. Love So Life's English chapter inventory is intact at 106 main plus five extras; Kainushi wa Akuma's MangaDex chapter inventory is still **11 labels short** of an independent 56-label English reader index. Neither public media redistribution permission nor official publisher-level image fidelity has been established.
