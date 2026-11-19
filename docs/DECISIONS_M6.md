# M6 decisions (19 November 2026)

- Windows retrieval uses the supported GitHub CLI (`gh run download`) and a fixed repository plus approved run and artefact names. It does not accept arbitrary content URLs, tokens or execute a shell.
- The public registry is a pointer to short-lived licensed artefacts; no local or cloud media is auto-deleted or overwritten.
- Existing outputs are skipped **only after** full export validation, origin/licence checks and exact CBZ SHA-256 matches; corrupted destinations fail closed.
- Each independent export is validated before building an offline portable ZIP. A manifest records SHA-256 checksums of all ZIP members and a second verification pass reads the full package back.
- The newly identified creator-authorised Japanese manga *Give My Regards to Black Jack* has separate author attribution and post-publication reporting conditions. It is researched, not yet an enabled remote adapter.
