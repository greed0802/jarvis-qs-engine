# JARVIS v5.0.0-alpha.35.5 Change Report

Base: v5.0.0-alpha.35.4

Scope: Active-task Workbook Read Policy Non-mutating Route Ownership.

Changed:
- `jarvis_v5/router/active_task_language_gate.py`
  - Added active-task workbook-read policy/help detector.
  - Routes alpha.35 workbook-read policy vocabulary to `active_task_non_mutating_language`.
  - Category: `workbook_read_policy_help`.
- `jarvis_v5/tests/smoke/test_alpha35_5_active_workbook_read_policy_non_mutating.py`
  - Added targeted active-task non-mutating route tests.

No workbook access, Builder engine, parser, slot reducer mutation logic, Formatter, QA, O&A, UI, Output Center, registry execution flags, safe path resolver, workbook preflight, or preview policy was changed.
