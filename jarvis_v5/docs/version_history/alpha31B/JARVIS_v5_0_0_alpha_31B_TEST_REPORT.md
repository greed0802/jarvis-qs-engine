# JARVIS v5.0.0-alpha.31B Test Report

## Standard regression

- `python -m compileall -q jarvis_v5`: PASS
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`: PASS — 243 passed
- Standard JSON packs: PASS — 32 / 32 packs
- Standard JSON pack tests: PASS — 132 / 132 tests

## Targeted weakness subset

- 015–019 `generic_choose_tool_ambiguity`: PASS — 250 / 250 tests
- 084–089 `prompt_injection_no_active_no_execution`: PASS — 300 / 300 tests
- Total targeted subset: PASS — 11 / 11 packs, 550 / 550 tests

## Safety aggregate

- `workbook_read_any_true=false`
- `engine_called_any_true=false`
- `excel_created_any_true=false`
- `legacy_builder_called_any_true=false`

## Static scans

- Duplicate FastAPI routes: 0
- Same-file top-level duplicate definitions: 0
- Cross-file helper/function duplicates: 33 documented only
- Protected Builder boundary hash check: PASS — 10 / 10 unchanged

## Not performed

- Windows `.bat` scripts were created but not run on Windows.
- UI/browser testing was not performed.
- Full workbook read/engine/export testing was not performed because execution remains disabled.
