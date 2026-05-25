# Jarvis v5.0.0-alpha.33.1 Test Report

Status: PASS after targeted and chunked verification.

## Test groups
- Targeted 4 failed Windows path-owner tests: PASS, 4 / 4 passed.
- Compile check: PASS.
- Smoke pytest suite: PASS in clean chunks, 275 / 275 tests passed.
- Built-in JSON packs: PASS, 38 / 38 packs, 174 / 174 tests passed.

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

## Note
A monolithic pytest run timed out in the sandbox, so the smoke suite was rerun in clean file chunks. A stale pending-clarification failure from previous partial/timed runs was resolved by cleaning runtime data; clean chunks then passed.
