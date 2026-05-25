# Jarvis v5.0.0-alpha.35.3 Test Report

## Results

- Targeted alpha35.2 sanitization tests: 6 / 6 passed
- Sensitive regression tests: 30 / 30 passed
- Full pytest: 296 / 296 passed
- Built-in JSON pack sweep: 40 / 40 packs passed
- Attack pack 004: completed, no HTTP status 0 exceptions, 47 / 50 passed; remaining 3 are safe `normal_id_*` preservation expectations from the external attack pack
- Attack pack 005: completed, no HTTP status 0 exceptions, 47 / 50 passed; remaining 3 are safe `normal_id_*` preservation expectations from the external attack pack

## Safety aggregate

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false
