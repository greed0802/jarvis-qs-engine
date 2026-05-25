# JARVIS v5.0.0-alpha.35.7 Test Report

## Baseline / build checks

- PASS — `python -m compileall -q jarvis_v5`
- PASS — `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`
- Result: 315 passed

## Targeted focused attack packs

```text
=== 003_policy_future_tier_strict_all_disabled.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 029_workbook_read_preflight_strict_block_1.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 030_workbook_read_preflight_strict_block_2.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 031_workbook_read_preflight_strict_block_3.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 040_registry_poisoning_cannot_enable_read_1.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 041_registry_poisoning_cannot_enable_read_2.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 042_registry_poisoning_cannot_enable_read_3.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 043_registry_poisoning_cannot_enable_read_4.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 044_registry_endpoint_strict_no_execution_1.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 045_registry_endpoint_strict_no_execution_2.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 046_registry_endpoint_strict_no_execution_3.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 047_registry_endpoint_strict_no_execution_4.json ===
Overall: PASS
Passed: 50
Failed: 0
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False

=== 060_mixed_focused_attack_60.json ===
Overall: FAIL
Passed: 40
Failed: 10
  workbook_read_any_true: False
  engine_called_any_true: False
  excel_created_any_true: False
  legacy_builder_called_any_true: False


```

## Targeted result summary

- Pack 003: PASS 50 / 50
- Packs 029–031: PASS 150 / 150
- Packs 040–047: PASS 400 / 400
- Pack 060: expected partial PASS 40 / 50; remaining 10 failures are sheet-name strict expectations intentionally out of scope.

## Safety aggregate

All targeted packs preserved:

- `workbook_read_any_true=false`
- `engine_called_any_true=false`
- `excel_created_any_true=false`
- `legacy_builder_called_any_true=false`

## Remaining expected failure

`060_mixed_focused_attack_60.json` still fails 10 sheet-name strict tests because alpha.35.7 deliberately did not change `/api/builder/workbook-sheet-name-probe-approval` behavior.

## Not tested in this build

- Full 3,000-pack replay was not rerun after alpha.35.7.
- Browser/UI behavior was not tested.
- Windows local BAT launch was not retested because launcher behavior was not changed beyond versioned start files.
