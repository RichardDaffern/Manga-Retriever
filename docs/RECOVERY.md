# Recovery and data integrity

A failed local import removes its temporary staging directory and does not publish an incomplete export. The identity registry is written via a temporary file and atomic replacement under an exclusive `.lock`; never delete a lock before checking that no other import runs. Existing output is never intentionally replaced.

Repeat the import into a **new** output directory with the same registry. Verify each export with `python -m manga_retriever verify --export DIR`. Keep a private backup of `ids.json`, original input files and validated export. If a file has changed, a different page ID is expected; never silently restore reading progress to a new image.

Remote retry/checkpoint/partial export handling is **planned for M4/M5**, not available in M1/M2.
