# Formats and data contracts

The `controller_candidate/` directory matches the local Controller's candidate v1: `catalogue.json` as `MangaEntry[]`, `inventory.json` with `controllerCandidateVersion: 1`, `manifests/ch_*.json` with `schemaVersion: 1`, `mediaKind: manga`, chapter ID and verified page records, and `assets/manga/mng_.../ch_.../pg_....ext` with original image bytes.

Page records contain `id`, `assetPath`, `mimeType`, dimensions, `byteSize` and lowercase SHA-256; chapter records contain immutable `id`, label, zero-based sequence, optional volume and pageCount. Personal notes/ratings/progress never enter the export. `rights.json` is optional private SourceRights v1. It remains a declaration, not independent rights verification. `download_manifest.json` outside the candidate contains only export counts and warning status.

Per-chapter CBZs are standard ZIP with natural order numbered pages and encoded original bytes. ZIP compression changes archive bytes, not page bytes. Unknown schema versions and unsupported formats fail closed.
