# Jarvis v5.0.0-alpha.31D Test Report

Base: v5.0.0-alpha.31B

## Standard regression

- `python -m compileall -q jarvis_v5`: PASS
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`: PASS — 249 passed
- JSON packs: PASS — 33 / 33 packs
- JSON pack tests: PASS — 136 / 136 tests

## Targeted weakness subset

- 020–024 active_non_mutating_state_first: PASS — 250 / 250
- 031–034 active_feedback_read_only: PASS — 200 / 200
- selected active-only minimal/mixed red-team subset: PASS — 10 / 10 tests

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```

## Static checks

- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Protected Builder boundary hash check: PASS — 10 / 10 unchanged
- Execution flags: `WORKBOOK_READ_ENABLED=False`, `BUILDER_ENGINE_EXECUTION_ENABLED=False`, `LEGACY_BUILDER_CALLABLE=False`, `EXCEL_OUTPUT_ENABLED=False`

## Notes

Windows `.bat` files were created but not run on Windows here.
