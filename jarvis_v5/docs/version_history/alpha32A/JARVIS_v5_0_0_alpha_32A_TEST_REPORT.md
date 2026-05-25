# Test Report — v5.0.0-alpha.32A

## Standard regression

- compileall: PASS
- pytest: PASS — 268 passed
- JSON packs: PASS — 37 / 37 packs
- JSON pack tests: PASS — 171 / 171 tests

## Targeted weakness subset

- 100–109 minimal_pair_route_ownership: PASS — 500 / 500

## Safety aggregate

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## Static scans

- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file helper/function duplicates: 29 documented only
- Protected Builder boundary hash check: PASS — protected execution files unchanged from scope perspective
