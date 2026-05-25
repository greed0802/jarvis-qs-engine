# Jarvis v5.0.0-alpha.33 Test Report

Status: PASS after clean chunked verification.

## Test groups
- Compile check: PASS
- Smoke pytest suite: PASS in clean chunks, 275 / 275 tests passed
- Built-in JSON packs: PASS, 38 / 38 packs, 174 / 174 tests passed
- Targeted alpha.33 smoke: PASS, 7 / 7 tests passed
- Targeted alpha.33 JSON pack: PASS, 3 / 3 tests passed

## Safety aggregate
- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## Static verification
- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file helper/function duplicates: 29 classified, runtime-risk duplicates: 0
- Protected Builder boundary hash check: 9 / 9 unchanged
- Registry execution files changed: 0
- Forbidden workbook libraries/calls in new module: 0
