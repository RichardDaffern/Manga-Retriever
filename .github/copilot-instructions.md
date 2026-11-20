# GitHub Copilot repository instructions

The canonical, full instructions for **all AI agents** in this public repository are in [AGENTS.md](../AGENTS.md). The detailed project purpose, source capability matrix, architecture, current evidence, data formats, Windows instructions, CI gates and handover requirements are in [docs/PROJECT_HANDBOOK.md](../docs/PROJECT_HANDBOOK.md). **Read both before working.**

Mandatory summary:

1. Work only on `RichardDaffern/Manga-Retriever` unless the owner separately authorises changes elsewhere; the Retriever packages local source media and **does not upload to the private Hugging Face dataset** or edit the Reader.
2. Use the **English-only Manga Library** policy by default. A specific non-English request is a narrow owner exception, never a licence to mislabel languages or automatically add Korean/Japanese pages to the English catalogue.
3. Require per-source download/retention/export terms and adequate rights evidence. No DRM, CAPTCHA, challenge or paywall circumvention; no copyrighted manga media or private rights records in public Actions artefacts, repository files or logs.
4. Preserve original image bytes for raster sources, chapter/page SHA-256, immutable IDs, complete verified CBZs and Controller candidate v1; fail closed on unsafe URLs/archives, partial chapters, incorrect languages and overwrites.
5. **Never confuse metadata/index success with actual media download.** Real Chapter 1 MangaKatana pilot covered five prior pinned titles and 246 verified image pages; a sixth Fairytale title added with an 8-page real pilot, **not complete English downloads**. MangaDex UUID `90f7c7a6-b759-4afb-b1cb-1af4660df307` has zero hosted chapters across languages.
6. Inspect the latest `main`, open PRs, workflows and logs. Make focused PRs with synthetic tests. Once all Windows/Linux/security checks pass, merge scoped non-destructive approved work without repeatedly asking the owner.
7. Keep work moving across independent source tracks in parallel, within rate limits. Report exact blockers, verified chapter/page counts, artefact retention, links and next steps. Do not claim work is ongoing without an actual scheduled job/automation.
8. Never broaden the public bulk source allowlist beyond `peppercarrot:26` without independent permission review and appropriate tests.

To resolve any conflict, trust current code plus verifiable run evidence, the owner-authorised security boundary and then the current canonical handbook/agent instructions, not old milestone prose.
