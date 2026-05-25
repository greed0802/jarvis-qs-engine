# Jarvis v5.0.0-alpha.32C.1 Test Report

## Result

PASS.

## Tests performed

```text
PASS - python -m compileall -q jarvis_v5
PASS - PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
Result: 268 passed

PASS - built-in JSON pack sweep
Result: 37 / 37 packs passed, 171 / 171 tests passed

PASS - duplicate FastAPI route scan = 0
PASS - same-file duplicate top-level definition scan = 0
PASS - cross-file duplicate scan visible/classified = 29 total, 0 runtime-risk
PASS - protected Builder boundary hash check = 9 / 9 unchanged
PASS - package root stale previous-version artifact scan = 0
PASS - registry execution flag scan = 0 enabled runtime execution flags
```

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```
