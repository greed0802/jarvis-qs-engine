# Current Backend Status — v5.0.0-alpha.30

Current version: `v5.0.0-alpha.30`

Base version: `v5.0.0-alpha.29`

Scope: Workbook Read Preflight Contract, still no workbook parse/output.

## Active safety locks

- `WORKBOOK_READ_ENABLED = False`
- `BUILDER_ENGINE_EXECUTION_ENABLED = False`
- `LEGACY_BUILDER_CALLABLE = False`
- `EXCEL_OUTPUT_ENABLED = False`

## New endpoint

- `POST /api/builder/workbook-read-preflight-dry-run`

## Route ownership

- Route exposure: `jarvis_v5/app.py`
- Preflight logic: `jarvis_v5/tools/builder/workbook_read_preflight_contract.py`
- Schema: `jarvis_v5/schemas/message_schema.py`

## Current behavior

The endpoint inspects Jarvis metadata store contract/workbook reference metadata only. It does not resolve, open, parse, or read workbook files.

## Dormant-code registry

Dormant-code preservation remains documented in `jarvis_v5/docs/DORMANT_CODE_REGISTRY_ALPHA_29.md`. No dormant/watchlist item was deleted, renamed, moved, or refactored in alpha.30.
