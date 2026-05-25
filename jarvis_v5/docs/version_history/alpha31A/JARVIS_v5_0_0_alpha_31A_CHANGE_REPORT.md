# Jarvis v5.0.0-alpha.31B Change Report

## Base
v5.0.0-alpha.30.1

## Scope
Response-shape compatibility only. No router behavior change, no parser behavior change, no workbook read.

## Files changed
- `jarvis_v5/config.py`
- `jarvis_v5/app.py`
- `jarvis_v5/tools/builder/preview_execution_policy.py`
- `jarvis_v5/tests/smoke/test_alpha31B_response_shape_compatibility.py`
- `jarvis_v5/tests/packs/alpha31B_response_shape_compatibility_tests.json`
- docs/reports/handoff/status files

## Functions changed
- `api_version()` metadata only
- `api_plan(...)` additive aliases only
- `no_active_task_plan_payload(...)` additive aliases only
- `_apply_chat_response_shape_compatibility(...)` new response-shape helper
- `api_chat(...)` calls response-shape helper only
- `workbook_read_permission_boundary(...)` additive alias only

## Response aliases added
- `/api/plan.version`
- `/api/plan.latest_snapshot`
- `/api/plan.latest_adapter`
- `/api/plan.latest_engine_contract`
- `/api/builder/preview-execution-policy.workbook_read_permission_boundary.workbook_read_enabled`
- `/api/chat.plan_mutated` deterministic field with true-mutation preservation

## Not touched
Router behavior, parser behavior, workbook read/open/parse, Builder engine, legacy Builder, Excel output, Formatter, QA, O&A, UI, Output Center, background jobs.
