# Test matrix

Local `unittest` tests cover: natural numeric page order; original PNG bytes in CBZ; Controller candidate shape; stable repeat import IDs; traversal and ZIP ratio rejection; fake MIME and duplicate pages; archive imports; no overwrites; corrupt export rejection; rights-schema fail-closed; missing page sequence warnings; CLI verify; damaged CBZs; orphaned files; missing archives; tampered page IDs; rights status inconsistencies; chapter ordering. Fixtures are synthetic Pillow images only.

`python -m unittest discover -s tests -v` and `python -m compileall -q manga_retriever tests` work offline when Pillow is installed. CI is configured for Windows/Linux Python 3.12 with a pip-audit and Ruff check, CI is subject to GitHub Actions completion. The security audit requires Pillow 13 or newer because Pillow 12.3.0 had published vulnerabilities. Live source and real Controller end-to-end tests have **not** run.

M3 adds 8 offline synthetic adapter tests (25 in total), including complete high-resolution link discovery, rights checks, anti-SSRF host checks, bounded retry classification, end-to-end JPEG packaging and partial-download refusal. Live source operation is separate from required CI, and succeeds only when a completed live workflow confirms it.

## M4 recovery regression gate

`tests/test_checkpoint.py` verifies atomic checkpoint state and reuse, interruption at a later page, corrupt-image re-download, plan/schema tampering, malformed checksums, concurrency locks, symlinks, unindexed files and oversized payloads. `tests/test_m4_peppercarrot.py` exercises the full authorised-source adapter offline with synthetic JPEG pages, including failed attempts and successful resumption. No real media is committed. Existing CI continues to check Python 3.12 Windows/Linux, Ruff and dependency vulnerabilities.

## M5 batch verification

`tests/test_batch.py` uses invented receipt data to test strict source selection, immutable GitHub artefact IDs/URLs, hash and expiry validation, source provenance, idempotent registry updates, duplicate rejection, fail-closed future versions, partial result retention and CLI workflow output. PR CI uses deterministic synthetic fixtures and verifies that missing jobs fail the batch without discarding completed registry entries. Real Pepper&Carrot downloads are exercised separately with the existing manual Single Manga Download or Bulk Manga Download Actions; external website downtime is not a deterministic CI gate. CI continues to require Python 3.12 tests on Windows and Linux, Ruff, and dependency audit.
