# Change Report — v5.0.0-alpha.35.5

## Base
v5.0.0-alpha.35.3.1

## Changed
- Added no-active sheet-name / worksheet-name / workbook-tab ambiguity detection in `no_active_task_language_gate.py`.
- Added targeted smoke tests for sheet-name ambiguity routing.
- Updated version and report metadata.

## Behavior
No-active sheet/tab requests now route to `choose_tool` with clarification instead of `general_stub` or `new_builder_task_shell`.

## Not changed
Workbook access, Builder engine, parser, Formatter, QA, O&A, UI, Output Center, registry execution flags, alpha.33 metadata probe, alpha.34 sheet-name probe endpoint, alpha.35 policy owner, safe path resolver, workbook read preflight, preview policy.
