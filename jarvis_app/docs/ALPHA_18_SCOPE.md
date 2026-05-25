# v5.0.0-alpha.18 — Response Consistency + Clarification Resolution Contract, no engine

## Scope

- Standardize no-engine safety fields across Builder endpoint responses.
- Include `legacy_builder_called=false` and nested `safety` where relevant.
- Standardize stale adapter contract block reason to `adapter_is_stale`.
- Preserve detailed `stale_reason=adapter_snapshot_mismatch` diagnostics.
- Make `clarification_resolved` a supported/testable route.
- Expose post-resolution reducer, trade registry, and normalization evidence.

## Safety boundary

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `contract_only=true`
- `legacy_builder_called=false`

## Explicitly not included

- No Builder engine call.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter.
- No QA logic beyond route/diagnostic cleanup.
- No O&A.
- No UI redesign.
- No current Jarvis replacement.
