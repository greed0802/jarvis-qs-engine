# Next Chat Handoff — v5.0.0-alpha.35.10.2

Use v5.0.0-alpha.35.10.2 as candidate after local validation. Rollback: v5.0.0-alpha.35.10.1 accepted checkpoint.

## Scope completed

The phrase `Rewrite this issue report: Preview is broken after MPa.` now routes to `active_task_non_mutating_language`, not `active_task_preview_stub` or `feedback_read_only`.

Real Preview commands still route to Preview. Real feedback like `Preview is broken after wall area.` still routes to `feedback_read_only`.

## Validation

- pytest: 338 passed
- alpha35.10.2 targeted pack: 3/3
- external engineering packs 07/37/38: 50/50 each
- safety flags false

## Remaining next validation

Rerun full external Phase 2 locally against alpha.35.10.2. Expected: 6,999 / 7,000, with the remaining failure as historical version-lock only.
