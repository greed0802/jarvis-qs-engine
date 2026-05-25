# v5.0.0-alpha.35.10.2 Change Report

Base: v5.0.0-alpha.35.10.1.

Scope: Active writing/report feedback wording should not trigger Preview or feedback routing.

## Runtime changes

- `jarvis_v5/router/active_task_action_language_gate.py`
  - Added a narrow writing/report-help guard before natural Preview/Export action matching.
- `jarvis_v5/router/feedback_router.py`
  - Added the same narrow writing/report-help guard to `is_explicit_standalone_feedback()`.
- `jarvis_v5/config.py`
  - Version/name metadata update to v5.0.0-alpha.35.10.2.

## Tests/packs added

- `jarvis_v5/tests/smoke/test_alpha35_10_2_active_writing_report_preview_false_positive.py`
- `jarvis_v5/tests/packs/alpha35_10_2_active_writing_report_preview_false_positive_tests.json`

## Test metadata

Built-in smoke/pack version locks were updated from alpha.35.10.1 to alpha.35.10.2 so the current package validates against its own version.

## Not touched

Builder formula/export engine, workbook access, Formatter, QA, O&A, UI, Output Center, preview policy, registry execution flags, Builder engine, snapshot/adapter endpoints, parser logic, and workbook policy runtime were not changed.
