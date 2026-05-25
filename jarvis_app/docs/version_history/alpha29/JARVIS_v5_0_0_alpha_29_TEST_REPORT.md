# Jarvis v5.0.0-alpha.29 Test Report

Generated: 2026-05-17T13:09:03.735028Z

## Results

- compileall: PASS
- pytest: PASS — 229 passed
- JSON packs: PASS — 28 / 28 packs
- JSON pack tests: PASS — 119 / 119 tests
- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file duplicate helper/function names: 33 documented only
- Protected Builder boundary hash check: 10 / 10 unchanged

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```

## Resolver safety

Alpha.29 smoke tests proved:

- internal contract can contain `saved_path`
- resolver response does not return the raw saved path value
- resolver response does not return forbidden exact raw path keys
- `path_resolved=false`
- `filesystem_checked=false`
- `workbook_filesystem_checked=false`
- `workbook_opened=false`
- `workbook_read=false`
