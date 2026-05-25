# JARVIS v5.0.0-alpha.35.5 Test Report

Results:
- Targeted alpha35.5 tests: 4 / 4 passed.
- Sensitive active/no-active regression tests: 25 / 25 passed.
- Full pytest by controlled chunks: 308 / 308 passed.
- Built-in JSON pack sweep: 40 / 40 packs, 180 / 180 tests passed.
- Attack packs 014-018: 250 / 250 passed.
- Regression packs 006-008: 150 / 150 passed.
- Regression packs 012-013: 100 / 100 passed.
- Regression packs 009-011: no `general_stub`, no `new_builder_task_shell`; remaining failures are known exact-route expectation conflicts.

Safety aggregate:
- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false
