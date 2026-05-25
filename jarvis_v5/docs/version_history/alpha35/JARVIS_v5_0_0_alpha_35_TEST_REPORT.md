# JARVIS v5.0.0-alpha.35.3 Test Report

## Results
- PASS — `python -m compileall -q jarvis_v5`
- PASS — `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`
- Result: 290 / 290 passed
- PASS — built-in JSON pack sweep
- Result: 40 / 40 packs passed, 180 / 180 tests passed

## Static checks
- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file helper/function duplicates: 31 classified, runtime-risk duplicates: 0
- Protected Builder boundary hash check: 9 / 9 unchanged
- Registry execution flags changed: 0
- openpyxl/load_workbook import/call only in `workbook_sheet_name_probe_approval.py`

## Safety aggregate
- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false
