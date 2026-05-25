# JARVIS v5.0.0-alpha.35.18 Change Report

## Version

`v5.0.0-alpha.35.18`

## Base

`v5.0.0-alpha.35.17`

## Scope

Workbook Read Permission Contract, metadata only, still no workbook read.

## Runtime/schema changes

- `jarvis_v5/config.py` — version bump only.
- `jarvis_v5/schemas/workbook_permission_contract_schema.py` — schema-only workbook permission contract.

## Registry metadata changes

- `jarvis_v5/registry/execution_policy_registry.json`
- `jarvis_v5/registry/capability_registry.json`
- `jarvis_v5/registry/tool_registry.json`
- `jarvis_v5/registry/file_requirement_registry.json`

## Tests added

- `jarvis_v5/tests/smoke/test_alpha35_18_workbook_permission_contract.py`
- `jarvis_v5/tests/packs/alpha35_18_workbook_permission_contract_tests.json`

## Docs/reports added

- `jarvis_v5/docs/ALPHA_35_18_SCOPE.md`
- `jarvis_v5/docs/WORKBOOK_READ_PERMISSION_CONTRACT.md`
- `jarvis_v5/docs/ROADMAP_AFTER_ALPHA_35_17.md`
- Alpha35.18 reports and handoff files.

## Not touched

- No app/router/reducer changes.
- No registry loader change.
- No Builder tool changes.
- No workbook reader runtime.
- No permission store runtime.
- No endpoint.
- No sheet-name probe.
- No workbook content/formula/cell read.
- No Builder engine.
- No Excel output.
