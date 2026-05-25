# Jarvis v5.0.0-alpha.28 Test Report

## Version
`v5.0.0-alpha.28`

## Base version
`v5.0.0-alpha.27`

## Test results

| Test | Result |
|---|---:|
| `python -m compileall -q jarvis_v5` | PASS |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` | PASS — 220 passed |
| JSON packs | PASS — 26 / 26 packs |
| JSON pack tests | PASS — 114 / 114 tests |
| Alpha.28 JSON pack | PASS — 4 / 4 tests |
| Protected Builder boundary hash check | PASS — 10 / 10 |
| Execution flag scan | PASS — no execution flag set to true |
| Duplicate FastAPI route scan | PASS — none found |
| Preview execution policy route owner scan | PASS — one FastAPI endpoint owner in `jarvis_v5/app.py` |

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```

## Confirmed no-engine status
Alpha.28 did not enable workbook reading, Builder engine execution, legacy Builder calling, Excel output, Formatter, QA Checker, O&A, UI execution, or background jobs.

## Notes
- The all-pack run was also saved in `alpha28_all_pack_results.json`.
- Existing baseline duplicate top-level helper/test names were observed as an informational scan result, not as duplicate route ownership.
