# Jarvis v5.0.0-alpha.31B Test Report

## Standard regression
- compileall: PASS
- pytest: PASS — 239 passed
- JSON packs: PASS — 31 / 31 packs
- JSON pack tests: PASS — 128 / 128 tests

## Targeted weakness response-shape subset
- Packs 066–069: PASS — 200 / 200 tests
- Packs 090–094: PASS — 250 / 250 tests
- Mixed red-team pack 110 plan_mutated path-presence: PASS — 0 path-not-found failures

## Safety aggregate
- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## Static checks
- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file helper/function names: 33 documented only
- Protected Builder boundary unchanged: 10 / 10
