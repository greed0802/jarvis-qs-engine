# Jarvis v5.0.0-alpha.30 Test Report

## Summary

- `python -m compileall -q jarvis_v5`: PASS
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`: PASS — 234 passed
- JSON packs: PASS — 29 / 29 packs
- JSON pack tests: PASS — 122 / 122 tests
- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file helper/function names: 33 documented only
- Workbook read preflight owner conflict: 0
- Protected Builder boundary hash check: PASS — 10 / 10 unchanged
- ZIP root inventory check: PASS

## Safety aggregate

- `workbook_read_any_true=false`
- `engine_called_any_true=false`
- `excel_created_any_true=false`
- `legacy_builder_called_any_true=false`

## Alpha.30-specific tests

- no-contract preflight blocks safely
- ready-contract preflight returns metadata-only workbook summary
- `.xlsx` candidate passes metadata extension policy
- `.xlsm` candidate passes metadata extension policy
- `.pdf`, `.zip`, and `.csv` candidates are rejected by metadata policy
- raw saved path value is not returned
- forbidden exact raw path keys are not returned
- workbook opened/read/parsed flags remain false
- sheet/cell/formula read flags remain false
- engine/Excel/legacy call flags remain false
