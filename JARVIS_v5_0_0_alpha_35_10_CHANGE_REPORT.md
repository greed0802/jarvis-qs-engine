# Jarvis v5.0.0-alpha.35.10 Change Report

Scope: No-active Mixed-language Workbook Policy Route Cleanup, no execution, no workbook read.

Base: v5.0.0-alpha.35.9
Fallback: v5.0.0-alpha.35.5.1

Runtime changes:
- `jarvis_v5/router/no_active_task_language_gate.py`
  - Added negative workbook-read polarity detection.
  - Allowed safe BOQ/Builder shell creation when a no-active request explicitly says not to read workbook contents.
  - Added narrow workbook-read policy aliases:
    - `Policy review please, no active task`
    - `Read the workbook policy, not the workbook`
    - `What does cells_read false mean?`
    - `Value engineering: read cells to optimize cost`
  - Added non-tool schedule guard for `Schedule a workbook read approval for later`.

Tests added:
- `jarvis_v5/tests/smoke/test_alpha35_10_no_active_mixed_language_policy_route.py`
- `jarvis_v5/tests/packs/alpha35_10_no_active_mixed_language_policy_route_tests.json`

No broad `Policy review please` alias was added.
