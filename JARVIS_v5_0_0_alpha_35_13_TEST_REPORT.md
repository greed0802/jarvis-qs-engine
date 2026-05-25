# Test Report — v5.0.0-alpha.35.13

## Commands run

```text
python -m compileall -q jarvis_v5
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_12_advisory_regression_hardening_tests.json --no-report
python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_11_capability_advisory_tests.json --no-report
python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_10_2_active_writing_report_preview_false_positive_tests.json --no-report
```

## Result

```text
compile: PASS
pytest: 349 passed
alpha35.12 advisory regression pack: 6 / 6
alpha35.11 capability advisory pack: 5 / 5
alpha35.10.2 active writing/report Preview false-positive pack: 3 / 3
```

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```
