# JARVIS v5.0.0-alpha.34 Test Report

## Results

- Targeted alpha.34 smoke tests: PASS — 9 / 9
- Smoke pytest suite in clean chunks: PASS — 284 / 284
- Built-in JSON pack sweep: PASS — 39 / 39 packs, 177 / 177 tests
- Targeted alpha.34 JSON pack: PASS — 3 / 3

## Safety aggregate

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## Note

A monolithic pytest run timed out in the sandbox, so the smoke suite was verified in clean file chunks.
