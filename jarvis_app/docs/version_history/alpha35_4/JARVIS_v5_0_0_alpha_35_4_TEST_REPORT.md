# Test Report — v5.0.0-alpha.35.5

## Passed
- targeted alpha35.4 sheet-name ambiguity tests: 2 / 2
- sensitive regressions: 12 / 12
- pytest controlled chunks: 304 / 304
- built-in JSON pack sweep: 40 / 40 packs, 180 / 180 tests
- attack 012: 50 / 50
- attack 013: 50 / 50
- attack 006-008: 50 / 50 each

## Expected conflict
- attack 009-011: 25 / 50 each. No `general_stub` or `new_builder_task_shell`; remaining exact route mismatches are prior pack-expectation conflicts.

## Safety
- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false
