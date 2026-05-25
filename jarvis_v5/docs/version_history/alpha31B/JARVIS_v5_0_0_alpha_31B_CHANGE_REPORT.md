# JARVIS v5.0.0-alpha.31B Change Report

## Version

- Version: `v5.0.0-alpha.31B`
- Base: `v5.0.0-alpha.31A`
- Scope: No-active generic ambiguity / prompt-injection route hygiene.
- Behavior boundaries: no active-task behavior change, no parser behavior change, no workbook read.

## Batches completed

- Batch 0 — baseline lock: passed.
- Batch 1 — version/docs: completed.
- Batch 2 — no-active generic ambiguity patterns: completed.
- Batch 3 — no-active prompt-injection safe-block detector: completed.
- Batch 4 — main router response for safe block: completed.
- Batch 5 — QA route allowlist: completed.
- Batch 6 — tests and JSON pack: completed.
- Batch 7 — targeted weakness subset report: completed.
- Batch 8 — reports/handoff: completed.
- Batch 9 — package cleanup before ZIP: completed.
- Batch 10 — final regression/package: completed.

## Runtime files changed

- `jarvis_v5/config.py`
- `jarvis_v5/router/no_active_task_language_gate.py`
- `jarvis_v5/router/main_router.py`
- `jarvis_v5/qa_runner/test_executor.py`

## Functions changed / added

- `classify_no_active_task_language(...)`
- `detect_generic_tool_ambiguity(...)`
- `detect_no_active_prompt_injection_safe_block(...)` — new.
- `MainRouter._no_active_task_language_gate_response(...)`

## Tests / packs added

- `jarvis_v5/tests/smoke/test_alpha31B_no_active_route_hygiene.py`
- `jarvis_v5/tests/packs/alpha31B_no_active_route_hygiene_tests.json`

## What was fixed

- No-active generic ambiguity phrases now route to `choose_tool` instead of `general_stub`:
  - `Do it safely.`
  - `Work on this attachment.`
  - `What tool should use this?`
- No-active prompt-injection-style requests now route to `no_active_prompt_injection_safe_block` instead of `general_stub`.
- The new safe-block response is blocked, metadata-only, non-executing, and does not echo the unsafe instruction text.

## What was not touched

- Active-task behavior.
- Parser/conflict behavior.
- Builder formula/export engine.
- CostX formula generation.
- Formula Integrity Guard execution.
- Legacy Builder execution bridge.
- Workbook reader/parser.
- Excel output writer.
- Slot reducer.
- Builder parser.
- Formatter / QA Checker / O&A / UI / Output Center.

## Safety locks

All remain false:

- `WORKBOOK_READ_ENABLED = False`
- `BUILDER_ENGINE_EXECUTION_ENABLED = False`
- `LEGACY_BUILDER_CALLABLE = False`
- `EXCEL_OUTPUT_ENABLED = False`
