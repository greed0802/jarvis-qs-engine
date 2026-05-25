# Bug Report — v5.0.0-alpha.35.5

Fixed: no-active sheet-name / worksheet-name / workbook-tab ambiguity previously fell to `general_stub` or accidentally started `new_builder_task_shell` for BOQ tab wording.

Safety impact: no workbook read, no sheet-name read, no cell/formula read, no engine call, no Excel output.

Remaining known gaps: active-task policy routing, pending clarification policy behavior, preflight wording, policy visibility in `/api/plan`, registry response-shape hardening.
