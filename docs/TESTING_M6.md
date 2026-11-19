# M6 Windows and artefact retrieval tests

`tests/test_retrieve.py` checks metadata allowlisting, expiry, GitHub CLI command construction without a shell, download/verify/atomic publish, verified skip-existing, corrupt pre-existing export refusal, checksum errors, failed CLI cleanup, symlink and unsafe output checks and ZIP consolidation with per-member SHA-256. All tests are synthetic and run on Python 3.12 in GitHub CI on Windows/Linux.

Live GitHub artefact download remains an operational/manual gate because a public repo may have zero current licensed artefact receipts and GitHub uploads expire. No actual licensed page data is stored in the tests or Git tree.
