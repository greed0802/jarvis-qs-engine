# Test Report — v5.0.0-alpha.35.14

Expected completed checks:

- `python -m compileall -q jarvis_v5` — PASS
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` — PASS, `355 passed`
- `alpha35_14_tool_contract_map_tests.json` — PASS, `6 / 6`
- `alpha35_12_advisory_regression_hardening_tests.json` — PASS, `6 / 6`
- `alpha35_11_capability_advisory_tests.json` — PASS, `5 / 5`
- `alpha35_10_2_active_writing_report_preview_false_positive_tests.json` — PASS, `3 / 3`

Safety aggregate stayed false for workbook read, engine call, Excel output, and legacy Builder call.
