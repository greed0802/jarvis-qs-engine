# v5.0.0-alpha.11 — Contract Negative Guards + Contract Replay Debug, no engine

## Scope

Alpha.11 strengthens the Builder engine contract boundary introduced in alpha.10. It focuses on negative guards and replay/debug inspection only.

## In scope

- Block contract creation for incomplete setup.
- Block contract creation for stale snapshots.
- Block contract creation for stale/missing/mismatched adapter dry runs.
- Block contract creation while pending clarification exists.
- Block contract creation for unresolved conflicts or normalization issues.
- Add contract replay/debug endpoints:
  - `GET /api/builder/engine-contract/{contract_id}`
  - `GET /api/builder/engine-contract/latest/{conversation_id}`
- Expose replay URL and latest blocked attempt details in `/api/plan/{conversation_id}`.
- Add clearer contract validation blockers.

## Out of scope

- No Builder engine.
- No workbook reading/parsing.
- No CostX formula generation.
- No Excel output.
- No Formatter, QA, or O&A.
- No UI redesign.
- No current Jarvis replacement.

## Required safety locks

- `workbook_read = false`
- `engine_called = false`
- `excel_created = false`
- `contract_only = true`
- `legacy_builder_called = false`
