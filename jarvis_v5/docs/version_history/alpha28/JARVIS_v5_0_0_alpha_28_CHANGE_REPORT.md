# Jarvis v5.0.0-alpha.28 Change Report

## Version
`v5.0.0-alpha.28`

## Base version
`v5.0.0-alpha.27`

## Build title
Policy Response Hygiene + Approval Token Readiness Contract, still no workbook read.

## Scope completed
Alpha.28 tightens the metadata-only preview/export policy response and adds governance/handoff continuity documents before any future workbook read or Builder execution work.

## Files changed

### Runtime / schema / policy
- `jarvis_v5/config.py`
- `jarvis_v5/app.py`
- `jarvis_v5/schemas/message_schema.py`
- `jarvis_v5/tools/builder/preview_execution_policy.py`
- `jarvis_v5/qa_runner/test_executor.py`

### Tests / packs
- `jarvis_v5/tests/smoke/test_alpha28_policy_response_hygiene_approval_readiness.py`
- `jarvis_v5/tests/packs/alpha28_policy_response_hygiene_approval_readiness_tests.json`
- Existing retained tests/packs were updated only for exact version/scope assertions where required.

### Docs / handoff / reports
- `README.md`
- `jarvis_v5/docs/ALPHA_24_1_SCOPE.md`
- `jarvis_v5/docs/ALPHA_26_1_SCOPE.md`
- `jarvis_v5/docs/ALPHA_28_SCOPE.md`
- `jarvis_v5/docs/JARVIS_PATCH_GOVERNANCE_RULES.md`
- `jarvis_v5/docs/PROTECTED_BUILDER_BOUNDARY_HASH_MANIFEST_ALPHA_28.md`
- `CURRENT_BACKEND_STATUS_v5_alpha_28.md`
- `NEXT_CHAT_HANDOFF_v5_alpha_28.md`
- `CHAT_CONTEXT_ARCHIVE_v5_alpha_28.md`
- `alpha28_all_pack_results.json`

## Functions changed
- `api_version` in `jarvis_v5/app.py`
- `evaluate_preview_execution_policy` in `jarvis_v5/tools/builder/preview_execution_policy.py`
- `validate_step_compatibility` logic in `jarvis_v5/qa_runner/test_executor.py` only for endpoint safety-field warning compatibility

## Functions added
In `jarvis_v5/tools/builder/preview_execution_policy.py`:
- `_count_or_zero`
- `_public_workbook_ref`
- `_public_contract_summary`
- `_approval_token_policy`
- `_preview_approval_readiness`
- `_export_approval_readiness`
- `_blocked_reason_details`
- `_contains_raw_path_key`

## What changed
- Normal `/api/builder/preview-execution-policy` responses now return `contract = null`.
- Public/scrubbed `contract_summary` is returned instead of the raw stored contract payload.
- `approval_token_policy` is defined but no token is issued.
- `preview_approval_readiness` and `export_approval_readiness` are returned as metadata-only readiness objects.
- `blocked_reason_details` gives machine-readable blocker detail.
- Version metadata now reflects alpha.28.
- Permanent patch governance and chat-context archive rules are documented.

## What was not touched
- Builder formula/export engine
- CostX formula generation
- Formula Integrity Guard execution
- Legacy Builder execution bridge
- Workbook reader/parser
- Excel writer/output generator
- Router core
- Slot reducer
- Builder parser
- Formatter
- QA Checker
- O&A
- UI
- Output Center
- Background jobs

## Safety locks
All remain disabled:

- `WORKBOOK_READ_ENABLED = False`
- `BUILDER_ENGINE_EXECUTION_ENABLED = False`
- `LEGACY_BUILDER_CALLABLE = False`
- `EXCEL_OUTPUT_ENABLED = False`

## Remaining risks
- Windows `.bat` launch scripts were not renamed in this scoped patch.
- Existing baseline duplicate top-level helper/test names remain informational and were not changed because they are outside the alpha.28 code family.
- No browser/UI test was performed.

## Next recommended dry run
`v5.0.0-alpha.29 — Safe Workbook Path Resolver Dry Run, still no workbook open/read.`
