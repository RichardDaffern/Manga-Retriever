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

## Verified 19 November 2026, first live audit

Results are from [Actions run 44549436127](https://github.com/RichardDaffern/Manga-Retriever/actions/runs/44549436127), with an automatically repeated run following the follow-up code changes.

| Title | English feed entries | Main numbered chapters found | Initial original-quality manifest | Preliminary suitability |
| --- | ---: | --- | --- | --- |
| Kainushi wa Akuma | 45 | 10 integer labels, 35 decimal labels; several numbering gaps | 34 page paths | **Partial/fragmented numbering**; needs mapping |
| Kimi no Iru Machi | 0 | None | Not available | **Unavailable in MangaDex English feed** |
| Last Game | 77 | **56/56**, plus 21 decimal extras | 41 page paths | **Promising** |
| Love Hina | 2 | Only chapters 1–2 | **0 hosted page paths** in sample | **Not a useful complete hosted source** |
| Lovely Complex | Two catalogue editions (standard / digital colour) | Edition-specific follow-up pending | Edition-specific follow-up pending | **Needs edition comparison** |
| Mado kara Madoka-chan | 0 | None | Not available | **Unavailable in MangaDex English feed** |
| Nisekoi | 5 | Only 5 integer chapter labels, reaching number 229 | **0 hosted page paths** in sample | **Not a useful complete hosted source** |
| Onizuka-chan and Sawarida-kun | 76 | **49/49**, plus 24 unique decimal extras | 4 page paths | **Promising**, source sample is short four-panel pages |

A page-path manifest means only that MangaDex lists high-quality image paths for that sampled chapter; **none of these jobs downloaded or archived artwork**. Integer chapter counts are an approximation of completeness, not proof that all publishers' extras or releases are covered.

For sources with no English feed, external licensed publisher editions may still be available, but this audit makes no download-permission claims.
