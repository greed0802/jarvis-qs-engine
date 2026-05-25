# JARVIS v5.0.0-alpha.35.10 Test Report

## Compile / pytest

- PASS — python -m compileall -q jarvis_v5
- PASS — pytest chunk 1: 173 passed
- PASS — pytest chunk 2: 152 passed
- Total smoke coverage: 325 passed

## Targeted pack

- PASS — alpha35_10_pending_clarification_policy_action_ownership_tests: 6 / 6

## Diagnostic old packs

- 048: partial; remaining failures include old pack expectations and policy-review allowed vs older block expectation.
- 051: partial; remaining failures include low-risk auto trade expectation mismatches.

## Safety

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false
