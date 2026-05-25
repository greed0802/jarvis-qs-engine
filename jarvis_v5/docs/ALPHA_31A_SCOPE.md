# v5.0.0-alpha.31B Scope

Response-shape compatibility only.

## Scope
- Add /api/plan compatibility aliases: version, latest_snapshot, latest_adapter, latest_engine_contract.
- Add workbook_read_enabled alias beside workbook_read_permission_boundary.enabled.
- Add chat response-shape compatibility for plan_mutated without changing routing or reducer behavior.

## Out of scope
- Router behavior changes.
- Parser behavior changes.
- Workbook read/open/parse.
- Builder engine, legacy Builder, Excel output, Formatter, QA, O&A, UI changes.
