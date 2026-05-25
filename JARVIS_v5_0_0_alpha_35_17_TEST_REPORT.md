# JARVIS v5.0.0-alpha.35.17 Test Report

JARVIS v5.0.0-alpha.35.17 TEST RUN RESULTS

PASS - python -m compileall -q jarvis_v5
PASS - PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
Result: 374 passed

PASS - alpha35.17 source authority hardening pack: 10 / 10
PASS - alpha35.16 document contract pack: 8 / 8
PASS - alpha35.15 job/output contract pack: 8 / 8
PASS - alpha35.14 tool contract map pack: 6 / 6
PASS - alpha35.12 advisory regression pack: 6 / 6
PASS - alpha35.10.2 active writing/report Preview false-positive pack: 3 / 3

Safety aggregate:
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false


Protected Builder boundary: 10 / 10 unchanged.

Registry flag scan:

- execution_enabled=true: 0
- document_read=true: 0
- ocr_enabled=true: 0
- rag_enabled=true: 0
- web_lookup_enabled=true: 0
- standards_ingestion_enabled=true: 0
- workbook_read=true: 0
- tool_execution_called=true: 0
- can_claim_compliance=true: 0
- can_certify_compliance=true: 0
