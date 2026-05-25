# Current Backend Status — v5.0.0-alpha.31B

Scope: Response-shape compatibility only.

Safety locks remain false: workbook read, Builder engine execution, legacy Builder callable, Excel output.

Runtime behavior changed only by additive response fields:
- /api/plan aliases: version, latest_snapshot, latest_adapter, latest_engine_contract.
- preview policy alias: workbook_read_permission_boundary.workbook_read_enabled=false.
- /api/chat plan_mutated compatibility default with true-mutation preservation.

Deferred: router and parser weakness families.
