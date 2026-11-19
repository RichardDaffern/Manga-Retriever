# Test matrix

Local `unittest` tests cover: natural numeric page order; original PNG bytes in CBZ; Controller candidate shape; stable repeat import IDs; traversal and ZIP ratio rejection; fake MIME and duplicate pages; archive imports; no overwrites; corrupt export rejection; rights-schema fail-closed; missing page sequence warnings; CLI verify. Fixtures are synthetic Pillow images only.

`python -m unittest discover -s tests -v` and `python -m compileall -q manga_retriever tests` work offline when Pillow is installed. CI is configured for Windows/Linux Python 3.12 with a pip-audit and Ruff check, but CI success must be confirmed after GitHub access is enabled. Live source and real Controller end-to-end tests have **not** run.
