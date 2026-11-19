# Love So Life / Kainushi wa Akuma: bounded image-quality pilot

The [ephemeral image-quality Actions workflow](../.github/workflows/love-kainushi-image-quality.yml) takes at most **two English chapters per exact title** and at most **one page per chapter** in each of the MangaDex *original-uploaded* and *data-saver* modes.

The comparison uses the official MangaDex@Home image server response. For each sample it checks JPEG/PNG/WebP decoding, width, height, byte count, image format, pixel count and SHA-256 in volatile job memory only. Source image bytes are **not committed, cached, saved or uploaded** as GitHub Actions artefacts; the output contains metrics and hashes only.

- HTTPS @Home hosts are restricted to MangaDex DNS names, redirecting is disabled, filenames and page hashes are validated, and per-page network and decoded pixel quotas apply.
- A quality comparison only tells us whether *MangaDex's uploader-original image* has more pixels or storage bytes than its data-saver version. It **cannot establish identity with a publisher's originals** or a scanlator's quality claims.
- Work remains subject to the API [acceptable-use policy](https://gitlab.com/mangadex-pub/mangadex-api-docs/-/blob/main/index.md) and copyright holders. The workflow never assumes that browsing or temporary decoding establishes permission to retain or redistribute full chapters.
- The offline inventory findings in [LOVE_KAINUSHI_READINESS.md](LOVE_KAINUSHI_READINESS.md) remain independently valid. No automatically redistributable full-title CBZ packages are enabled here.

The output artefact is **metrics only** and expires after seven days. A failed sample must remain clearly marked and cannot be called quality-verified.
