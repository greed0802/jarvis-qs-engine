# Jarvis v5.0.0-alpha.35.11 Test Report

## Commands run

```text
python -m compileall -q jarvis_v5
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_11_capability_advisory_tests.json --no-report
python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_10_2_active_writing_report_preview_false_positive_tests.json --no-report
```

## Results

```text
compileall: PASS
pytest: 343 passed
alpha35.11 targeted pack: PASS, 5 passed / 0 failed
alpha35.10.2 writing/report Preview false-positive regression pack: PASS, 3 passed / 0 failed
```

## Targeted regression coverage

- Builder-start still creates Builder shell: PASS.
- Preview without active task does not become advisory: PASS.
- Direct workbook read still safe-blocks: PASS.
- Future tool run requests stay metadata-only / blocked: PASS.
- alpha35.10.2 writing/report Preview false-positive remains fixed: PASS.

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```

## Protected hash result

```text
10 / 10 protected Builder boundary files unchanged
```
