# Supported sources

**Implemented:** local folders, ZIP and CBZ archives supplied by the owner. Supported image formats PNG/JPEG/WebP and AVIF if Pillow supports the codec. This does not confirm ownership or licence.

**Proposed / not implemented:** Pepper&Carrot licensed web acquisition, MangaDex metadata-only research, selected NDL public-domain media and individually licensed creator archives. See [source research](SOURCE_RESEARCH.md). No arbitrary website or API URL can be downloaded using this version.

## Implemented licensed webcomic pilot

Pepper&Carrot Episode 26 (English high-resolution 6 pages) uses a fixed official source-page/URL allowlist and CC BY 4.0 licence check. All other episodes and websites remain unimplemented. The resulting package records exact URL/hash per page in `download_manifest.json` and preserves required attribution. No unofficial manga source has download support.
