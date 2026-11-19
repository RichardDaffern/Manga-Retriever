# Test matrix

Local `unittest` tests cover: natural numeric page order; original PNG bytes in CBZ; Controller candidate shape; stable repeat import IDs; traversal and ZIP ratio rejection; fake MIME and duplicate pages; archive imports; no overwrites; corrupt export rejection; rights-schema fail-closed; missing page sequence warnings; CLI verify; damaged CBZs; orphaned files; missing archives; tampered page IDs; rights status inconsistencies; chapter ordering. Fixtures are synthetic Pillow images only.

`python -m unittest discover -s tests -v` and `python -m compileall -q manga_retriever tests` work offline when Pillow is installed. CI is configured for Windows/Linux Python 3.12 with a pip-audit and Ruff check, CI is subject to GitHub Actions completion. The security audit requires Pillow 13 or newer because Pillow 12.3.0 had published vulnerabilities. Live source and real Controller end-to-end tests have **not** run.

M3 adds 8 offline synthetic adapter tests (25 in total), including complete high-resolution link discovery, rights checks, anti-SSRF host checks, bounded retry classification, end-to-end JPEG packaging and partial-download refusal. Live source operation is separate from required CI, and succeeds only when a completed live workflow confirms it.
