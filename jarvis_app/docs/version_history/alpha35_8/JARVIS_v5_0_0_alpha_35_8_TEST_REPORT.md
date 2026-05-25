# Jarvis v5.0.0-alpha.35.8 Test Report

## Tests performed

- PASS — `python -m compileall -q jarvis_v5`
- PASS — pytest smoke suite in two chunks due sandbox timeout limits:
  - chunk 1: 181 passed
  - chunk 2: 138 passed
  - total: 319 passed
- PASS — `alpha35_8_workbook_read_policy_plan_visibility_tests.json`
  - 3 passed / 0 failed

## Optional old strict pack diagnostics

Old packs were replayed as diagnostics only. They still fail only because they expect `readiness.status = workbook_read_policy_reviewed`, while alpha.35.8 intentionally keeps `readiness.status = contract_ready` and adds additive policy fields.

- 032: 0 / 50, old version/status expectation only
- 035: 0 / 50, old readiness.status expectation only
- 038: 0 / 50, old readiness.status expectation only

## Safety

All targeted packs kept:

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false
