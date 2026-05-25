# Jarvis v5.0.0-alpha.35.12 Test Report

## Commands run

```text
python -m compileall -q jarvis_v5
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_12_advisory_regression_hardening_tests.json --no-report
python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_11_capability_advisory_tests.json --no-report
python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_10_2_active_writing_report_preview_false_positive_tests.json --no-report
```

## Results

```text
compileall: PASS
pytest: 349 passed
alpha35.12 targeted pack: 6 passed / 0 failed
alpha35.11 targeted pack: 5 passed / 0 failed
alpha35.10.2 writing/report Preview false-positive pack: 3 passed / 0 failed
```

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```

## Regression coverage

Confirmed:

- Future-tool run requests stay metadata-only and blocked.
- Unknown scope advisory requires clarification and does not start Builder.
- Known QS scopes do not trigger unknown-scope clarification.
- Builder-start still creates Builder shell.
- Preview without active task does not become advisory.
- Direct workbook-read request remains safe-blocked.
- Alpha35.10.2 writing/report Preview false-positive remains fixed.
