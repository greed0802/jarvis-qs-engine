# Jarvis v5.0.0-alpha.28.1 Test Report

## Version

`v5.0.0-alpha.28.1`

## Base

`v5.0.0-alpha.28`

## Scope

Package Artifact Deduplication + Helper Duplicate Audit, no behavior change.

## Test results

| Check | Result |
|---|---|
| `python -m compileall -q jarvis_v5` | PASS |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` | PASS — 225 passed |
| JSON packs | PASS — 27 / 27 packs |
| JSON pack tests | PASS — 116 / 116 tests |
| Duplicate FastAPI route scan | PASS — 0 duplicates |
| Same-file top-level duplicate definition scan | PASS — 0 duplicates |
| Cross-file duplicate helper/function scan | INFO — 33 documented |
| Preview-policy owner scan | PASS |
| Previous-version root artifact scan | PASS — 0 stale alpha.27/alpha.28 root artifacts |
| Protected Builder boundary hash check | PASS — 10 / 10 unchanged |
| Execution flag scan | PASS |

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```

## Notes

Cross-file helper duplicates are documented only in alpha.28.1. No helper renames or runtime behavior changes were made.
