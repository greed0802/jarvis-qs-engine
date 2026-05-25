# Test Report — v5.0.0-alpha.36.1

PASS — `python -m compileall -q jarvis_v5`

PASS — targeted pytest smoke set: 61 passed

PASS — alpha36.1 workbook metadata probe plan pack: 8 / 8
PASS — alpha36.0 integrity contract pack: 8 / 8
PASS — alpha35.19 workbook permission evidence-lock pack: 8 / 8
PASS — alpha35.18 workbook permission contract pack: 8 / 8
PASS — alpha35.17 source authority hardening pack: 10 / 10
PASS — alpha35.16 document contract pack: 8 / 8
PASS — alpha35.15 job/output contract pack: 8 / 8
PASS — alpha35.14 tool contract map pack: 6 / 6
PASS — alpha35.12 advisory regression pack: 6 / 6
PASS — alpha35.10.2 active writing/report Preview false-positive pack: 3 / 3

The single full `pytest -q` smoke command can exceed the sandbox execution window, so the retained critical suite was run through targeted pytest and JSON packs.

Safety aggregate: workbook_read=false, engine_called=false, excel_created=false, legacy_builder_called=false.
