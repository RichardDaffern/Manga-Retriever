# Three manga English original-upload-quality downloads

The following MangaDex title IDs were confirmed through the prior metadata-only source scans on 19 November 2026:

| Manga | Main numbered chapter ranges | English feed evidence | MangaDex ID |
| --- | --- | --- | --- |
| Kaichou wa Maid-sama! | 1–85 | 85/85 main chapters and 15 decimal extras | `d5e2bd89-e300-4262-a799-fb4f79bdb777` |
| Last Game | 1–56 | 56/56 main chapters and 21 decimal extras | `32600d3f-a43a-4f90-8a4e-c4e09f35c99b` |
| Onizuka-chan and Sawarida-kun | 1–49 | 49/49 main chapters and 24 decimal extras | `96b87943-6458-4045-a029-d3185d5cea57` |

The source selection and English originals are fixed in `manga_retriever/selected_sources.py` and cannot be overridden with arbitrary URLs. The GitHub workflow splits all **190 numbered main chapters** into eleven independent ranges of at most 20 chapters, with a maximum of two running concurrently. On a branch push it schedules **all eleven** automatically; a new user message is unnecessary to trigger later batches.

Each job runs a pinned downloader, verifies every CBZ and image, validates **individual main chapter labels** from output filenames (decimal extras do not substitute for missing numbered chapters), and copies verified CBZs plus checksum/size/dimension audit to a seven-day Actions artefact. No media is committed to git or sent to Hugging Face.

- Automatic GitHub Actions download: [Three Manga English Original-Quality Downloads](../.github/workflows/three-manga-download.yml)
- Automatic failed-job reruns: [Three Manga Batch Recovery](../.github/workflows/three-manga-recovery.yml), maximum two retries per run, no manual prompt needed
- The download requires manga artwork to be available at the source and access to comply with the source's terms. The job does not bypass login, paywalls or DRM.

**Important:** Main chapter filename validation, CBZ hashes and image decoding confirm file integrity, not publisher-master resolution, complete extras, legal download rights or quality of translations. Actions artefacts in this **public** repository may be readable by other users; they are not private simply because the owner is the intended recipient. Attribution for the source and scanlation groups is retained in each artefact.

Download successful artefacts via GitHub Actions before their seven-day expiry. Do not treat a failed or absent artefact as complete. The results cannot be automatically uploaded to a private Hugging Face repository without separate approval and a secure controller integration.
