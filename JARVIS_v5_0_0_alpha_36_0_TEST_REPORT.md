# Jarvis v5.0.0-alpha.36.0 Test Report

## Commands / Results

- PASS: `python -m compileall -q jarvis_v5`
- Controlled pytest smoke suite: 394 collected; smoke files run in isolated batches / file runs with data cleanup.
- PASS: alpha36.0 integrity contract pack: 8 / 8
- PASS: alpha35.19 workbook permission evidence-lock pack: 8 / 8
- PASS: alpha35.18 workbook permission contract pack: 8 / 8
- PASS: alpha35.17 source authority hardening pack: 10 / 10
- PASS: alpha35.16 document contract pack: 8 / 8
- PASS: alpha35.15 job/output contract pack: 8 / 8
- PASS: alpha35.14 tool contract map pack: 6 / 6
- PASS: alpha35.12 advisory regression pack: 6 / 6
- PASS: alpha35.10.2 active writing/report Preview false-positive pack: 3 / 3

The single full `pytest -q` command exceeded the sandbox execution window, so the same collected smoke suite was run in controlled isolated batches/files.

## Safety aggregate

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false
