# JARVIS v5.0.0-alpha.35.18 Test Report

## Result

PASS.

## Compile

```text
PASS - python -m compileall -q jarvis_v5
```

## Pytest

The smoke test suite was run in controlled file batches because the single full `pytest -q` command exceeded the sandbox execution-window timeout. The batched run covered the complete collected smoke suite.

```text
381 / 381 passed
```

## Targeted packs

```text
alpha35.18 workbook permission contract: 8 / 8
alpha35.17 source authority hardening: 10 / 10
alpha35.16 document contract: 8 / 8
alpha35.15 job/output contract: 8 / 8
alpha35.14 tool contract map: 6 / 6
alpha35.12 advisory regression: 6 / 6
alpha35.10.2 active writing/report Preview false-positive: 3 / 3
```

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```
