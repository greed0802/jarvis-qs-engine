# Chat Context Archive — v5.0.0-alpha.30

This archive captures safe user-visible context for continuity.

## Active governance

- Diagnose and plan first.
- Patch only after explicit FIRE/proceed approval.
- One route owner.
- One code family per batch.
- Batch 0 baseline first.
- If any batch fails, stop, fix that batch only, and retest from Batch 0.
- Sensitive files isolated.
- Clean package root before final ZIP.
- Future handoffs must include enough context to avoid lost Jarvis development state.

## Current build

The user approved FIRE for `v5.0.0-alpha.30` with scope: Workbook Read Preflight Contract, still no workbook parse/output.

## Important decisions

- Alpha.30 may inspect Jarvis metadata store contract data.
- Alpha.30 must not resolve, check, open, parse, or read workbook files.
- Raw path values and forbidden exact raw path keys must not appear in normal response.
- Dormant code must be preserved and documented, not deleted.

## Next recommended path

Dry run alpha.31 for the next approval/metadata stage before any real workbook read or parsing.
