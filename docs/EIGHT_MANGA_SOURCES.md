# Eight additional manga: availability and download feasibility

A metadata-only [GitHub Actions audit](../.github/workflows/source-probe-eight.yml) checks the following user-requested series:

1. Kainushi wa Akuma
2. Kimi no Iru Machi (A Town Where You Live)
3. Last Game
4. Love Hina
5. Lovely Complex (Love Com)
6. Mado kara Madoka-chan
7. Nisekoi (False Love)
8. Onizuka-chan and Sawarida-kun (Onizuka-chan to Sawarida-kun)

For each, the job first resolves an **exact** title/alternate-title match, rejects ambiguous similarly named series, paginates all MangaDex English chapter records, counts distinct numbered chapters and gaps, and checks only whether the first English chapter has an original-quality page manifest.

It retrieves **no image bytes**, creates no CBZ, and cannot establish the original publisher's resolution, the content's correctness, or permission to download or publicly redistribute artwork. The audit is separate from the ReLIFE 12-batch download, so it does not block or reset that run.

Result: [Workflow Actions runs](https://github.com/RichardDaffern/Manga-Retriever/actions/workflows/source-probe-eight.yml). Download the `eight-manga-english-source-report` metadata-only artefact and review `manga-source-audit-eight.json`. **Never infer that a chapter's existence in a fan-hosted reader authorises media rehosting.**
