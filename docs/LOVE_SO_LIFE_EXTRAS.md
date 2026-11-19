# Love So Life: five English extras

The main [six numbered chapter downloads](.github/workflows/love-so-life-download.yml) request chapters 1–106. The earlier live English feed additionally listed five distinct decimal chapter labels: **33.5, 33.6, 63.5, 75.5, 99.5**.

This separate [bonus-chapter workflow](../.github/workflows/love-so-life-extras-download.yml) resolves the exact five English chapter IDs from current MangaDex metadata, fetches each separately through the pinned downloader, and verifies its chapter-label filename, CBZ ZIP integrity and page image decoding/checksums.

A failure of one bonus chapter does not erase others. Verified files and a JSON missing-label audit are uploaded to GitHub Actions for seven days. The job fails if any of the five are missing, enabling the existing two-retry automatic recovery. Successful main numbered chapter batches are unaffected.

These are uploaded scanlator-supplied original quality, **not publisher-master image files**. Public workflow artefacts may be accessible to others. Respect original creator/scanlator rights, and do not assume an online chapter is licensed for redistribution.
