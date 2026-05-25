# Jarvis v5.0.0-alpha.31D Change Report

Base: v5.0.0-alpha.31B

Scope: Active non-mutating + feedback read-only ownership. No parser behavior change. No workbook read.

## Batches completed

- Batch 0 — baseline lock: passed
- Batch 1 — version/docs: completed
- Batch 2 — active non-mutating explanation signals: completed
- Batch 3 — active action explanation-steal guard: completed
- Batch 4 — feedback read-only marker expansion: completed
- Batch 5 — tests and JSON pack: completed
- Batch 6 — targeted weakness subset report: completed
- Batch 7 — reports/handoff: completed
- Batch 8 — package cleanup before ZIP: completed
- Batch 9 — final regression/package: completed

## Runtime files changed

- `jarvis_v5/config.py`
- `jarvis_v5/app.py` — version/scope metadata only
- `jarvis_v5/router/active_task_language_gate.py`
- `jarvis_v5/router/active_task_action_language_gate.py`
- `jarvis_v5/router/feedback_router.py`

## Tests added/updated

- `jarvis_v5/tests/smoke/test_alpha31C_active_non_mutating_feedback_read_only.py`
- `jarvis_v5/tests/packs/alpha31C_active_non_mutating_feedback_read_only_tests.json`
- retained exact version/scope assertions updated to v5.0.0-alpha.31D
- package hygiene test updated for alpha.31C root artifacts

## Functions changed

- `is_active_task_non_mutating_language(...)`
- `is_explicit_setup_command_text(...)` only to protect explicit concept-help wording from slot mutation
- `detect_active_task_action_language(...)` with a narrow explanatory-action guard
- `is_active_task_issue_feedback(...)`
- `api_version()` metadata only

## What changed

- Active Builder explanation/help phrases now route to `active_task_non_mutating_language`.
- Explanation phrases containing preview/export wording no longer get stolen by active action language unless they clearly ask to run/open/generate/export/download.
- Active task issue feedback phrases now route to `feedback_read_only` before action/slot reducer mutation.

## What did not change

- No parser behavior change.
- No pending-clarification behavior change.
- No workbook read, workbook parse, engine call, legacy Builder call, Excel output, Formatter, QA, O&A, UI, or Output Center behavior change.
