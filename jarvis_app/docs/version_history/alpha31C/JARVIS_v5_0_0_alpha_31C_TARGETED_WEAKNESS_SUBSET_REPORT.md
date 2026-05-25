# Targeted Weakness Subset Report — v5.0.0-alpha.31D

## Exact target families

- 020–024 `active_non_mutating_state_first`: PASS — 250 / 250
- 031–034 `active_feedback_read_only`: PASS — 200 / 200
- Selected active-only minimal/mixed red-team subset: PASS — 10 / 10

## Active action stability

Direct stability tests passed for:

- `Preview it please.` → `active_task_preview_stub`
- `Open preview.` → `active_task_preview_stub`
- `Export it.` → `active_task_export_stub`
- `Download output.` → current download/action route
- `Review current setup.` → `active_task_review`

## Slot reducer stability

Direct stability tests passed for:

- `Use Wall Types.` → `active_task_slot_edit`
- `Use Structural Steel.` → `active_task_slot_edit`
- `Unit m2.` → `active_task_slot_edit`

## Deferred / not included as alpha.31C failure

- Pending clarification risky-action phrase coverage
- Parser/function-unit conflict alias consolidation
- Windows BAT execution validation
