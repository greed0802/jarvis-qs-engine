# JARVIS v5.0.0-alpha.35.16 Test Report

## Tests performed
- PASS: python -m compileall -q jarvis_v5
- PASS: PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q — 367 passed
- PASS: alpha35.16 document contract pack — 8 / 8
- PASS: alpha35.15 job/output contract pack — 8 / 8
- PASS: alpha35.14 tool contract map pack — 6 / 6
- PASS: alpha35.12 advisory regression pack — 6 / 6
- PASS: alpha35.10.2 active writing/report Preview false-positive pack — 3 / 3

## Safety aggregate
- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false
- document_read_any_true=false by registry scan
- ocr_enabled_any_true=false by registry scan
- rag_enabled_any_true=false by registry scan

## Protected boundary
10 / 10 protected Builder boundary files unchanged.
