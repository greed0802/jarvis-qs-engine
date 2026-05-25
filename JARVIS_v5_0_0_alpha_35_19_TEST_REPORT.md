# JARVIS v5.0.0-alpha.35.19 Test Report

## Compile

PASS — `python -m compileall -q jarvis_v5`

## Pytest

The single full `pytest -q` command exceeded the sandbox execution-window timeout after partial progress. The same collected smoke suite was then run in controlled file batches.

PASS — controlled smoke suite: `387 / 387` passed.

Batch results:

```text
1-20: 112 passed
21-30: 47 passed
31-40: 50 passed
41-60: 107 passed
61-77: 71 passed
Total: 387 passed
```

## Targeted packs

```text
alpha35.19 workbook permission evidence-lock: 8 / 8 PASS
alpha35.18 workbook permission contract: 8 / 8 PASS
alpha35.17 source authority hardening: 10 / 10 PASS
alpha35.16 document contract: 8 / 8 PASS
alpha35.15 job/output contract: 8 / 8 PASS
alpha35.14 tool contract map: 6 / 6 PASS
alpha35.12 advisory regression: 6 / 6 PASS
alpha35.10.2 active writing/report Preview false-positive: 3 / 3 PASS
```

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```
