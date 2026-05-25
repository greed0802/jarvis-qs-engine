# JARVIS v5.0.0-alpha.35.3 Test Report

PASS - targeted alpha12 direct runner and dev endpoint tests: 2 / 2 passed.
PASS - package artifact current-root test: 1 / 1 passed.
PASS - python -m compileall -q jarvis_v5.
PASS - PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q: 290 / 290 passed.
PASS - built-in JSON pack sweep: 40 / 40 packs passed, 180 / 180 tests passed.
PASS - attack packs 004 and 005 complete without UnicodeEncodeError. Logical failures remain for future conversation_id sanitization.
PASS - duplicate FastAPI routes: 0.
PASS - same-file duplicate top-level definitions: 0.
PASS - protected Builder boundary hashes unchanged: 9 / 9.
PASS - registry execution flags unchanged.

Safety aggregate: workbook_read_any_true=false; engine_called_any_true=false; excel_created_any_true=false; legacy_builder_called_any_true=false.
