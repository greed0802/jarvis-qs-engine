# Jarvis v5.0.0-alpha.26.1 Test Report

## Compile / pytest

PASS — `python -m compileall -q jarvis_v5`

PASS — `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`

Result: 212 passed

## Full built-in JSON pack sweep

Total packs: 24

Total tests: 106

Passed: 106

Failed: 0

## Safety aggregate

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## Protected hash check

10 / 10 protected Builder boundary files unchanged.

## Package hygiene

Final package cleaned of `__pycache__`, `.pyc`, `.pytest_cache`, and generated runtime data files. Runtime data folders keep only `.keep` placeholders.
