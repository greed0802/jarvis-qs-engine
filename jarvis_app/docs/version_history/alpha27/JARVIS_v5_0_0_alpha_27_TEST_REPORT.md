# Jarvis v5.0.0-alpha.27 Test Report

## Checks
- PASS — `python -m compileall -q jarvis_v5`
- PASS — `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`
- Result: 216 passed
- PASS — retained JSON pack sweep
- Result: 25 / 25 packs passed, 110 / 110 tests passed
- PASS — protected Builder boundary hash check
- Result: 10 / 10 unchanged
- PASS — registry execution flag scan
- Result: execution_enabled=true count = 0
- PASS — duplicate route scan
- Result: none
- PASS — duplicate top-level class/function scan
- Result: none
- PASS — package hygiene cleanup before ZIP

## Safety aggregate
- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## Alpha.27 policy endpoint proof
`POST /api/builder/preview-execution-policy` returns route `builder_preview_execution_policy`, stays metadata-only, blocks execution, and reports all safety fields false.
