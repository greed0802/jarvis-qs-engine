# Duplicate Scan Report — v5.0.0-alpha.30

## Final scan summary

- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file helper/function names: 33 documented only
- Workbook read preflight owner conflict: 0
- Safe workbook path resolver owner preserved

## Workbook read preflight owner scan

Endpoint references:

- `jarvis_v5/app.py`
- `jarvis_v5/qa_runner/test_executor.py`
- `jarvis_v5/tests/smoke/test_alpha30_workbook_read_preflight_contract.py`

Runtime logic references:

- `jarvis_v5/app.py` exposes the endpoint and calls the owner
- `jarvis_v5/tools/builder/workbook_read_preflight_contract.py` owns the logic

Test references are ignored as owners.

## Cross-file helper duplicates

The count remains documented at 33. They were not changed in alpha.30 because this build is not a helper consolidation patch.

Allowed/test duplicates and watchlist runtime duplicates remain deferred according to the duplicate policy carried from alpha.28.1/alpha.29.
