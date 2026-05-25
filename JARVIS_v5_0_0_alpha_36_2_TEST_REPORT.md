# Test Report — alpha36.2

- PASS: `python -m compileall -q jarvis_v5`
- PASS: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` — 408 passed
- PASS: alpha36.2 dry-run JSON pack: 6 / 6
- PASS: alpha36.1 workbook metadata probe plan pack: 8 / 8
- PASS: alpha36.0 integrity contract pack: 8 / 8
- PASS: alpha35.19 workbook permission evidence-lock pack: 8 / 8
- PASS: alpha35.18 workbook permission contract pack: 8 / 8
- PASS: alpha35.12 advisory regression pack: 6 / 6
- PASS: alpha35.10.2 active writing/report Preview false-positive pack: 3 / 3

Safety aggregate remained false for workbook read, engine call, Excel creation, and legacy Builder call.
