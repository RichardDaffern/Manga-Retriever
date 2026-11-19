# Controller and Reader integration

Reference contracts: [Controller data contracts](https://github.com/AdityaSreevatsaK/Taiyou-Manga-Storage-Controller/blob/master/docs/DATA_CONTRACTS.md), [Reader types](https://github.com/AdityaSreevatsaK/Taiyous-Manga-Library/blob/master/src/domain/types.ts), [Reader ADR-006](https://github.com/AdityaSreevatsaK/Taiyous-Manga-Library/blob/master/docs/adr/006-manga-rights-and-private-asset-adapter.md).

The retriever produces `controller_candidate` for local inspection, and CBZs for archival readers. This mirrors Controller candidate v1 and does not add a parallel HF layout. Stable IDs follow the Controller algorithm, including SHA-256-based page identities. The Controller's real HF writes remain disabled. The Reader has no production private asset adaptor, cross-device sync or persistent manga library connection at present.

**End-to-end live Controller acceptance is pending:** validate a generated candidate using `python -m taiyou_manga verify --bundle ...` in an independently installed Controller. Back up the local registry before path changes. Do not copy private media into GitHub or start cloud migration without explicit owner approval and a rollback plan.
