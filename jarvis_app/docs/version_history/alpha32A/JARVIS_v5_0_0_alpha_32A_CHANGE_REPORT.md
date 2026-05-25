# Change Report — v5.0.0-alpha.32A

Base: v5.0.0-alpha.31F.1
Scope: Minimal Pair Route Ownership Hygiene, no parser behavior change, no workbook read.

## Runtime files changed

- jarvis_v5/config.py
- jarvis_v5/app.py
- jarvis_v5/router/feedback_router.py
- jarvis_v5/router/main_router.py
- jarvis_v5/router/no_active_task_language_gate.py
- jarvis_v5/qa_runner/test_executor.py

## Tests / pack changed

- jarvis_v5/tests/smoke/test_alpha32A_minimal_pair_route_ownership.py
- jarvis_v5/tests/packs/alpha32A_minimal_pair_route_ownership_tests.json
- retained version/scope assertions updated to v5.0.0-alpha.32A

## What changed

- Added narrow no-active standalone feedback markers for preview-broken wording.
- Added safe no-active action guard route: no_active_action_needs_active_task.
- Added no-active minimal-pair language coverage for Doors/Windows setup ambiguity.
- Added no-active help/clarification coverage for safe workbook path resolver wording and waterproofing checklist help.

## What did not change

- Parser behavior was not changed.
- Active-task behavior was not changed.
- Workbook read, Builder engine execution, legacy Builder call, and Excel output remain disabled.
