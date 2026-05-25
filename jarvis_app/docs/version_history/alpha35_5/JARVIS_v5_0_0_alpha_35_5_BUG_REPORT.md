# JARVIS v5.0.0-alpha.35.5 Bug Report

Fixed:
- Active-task workbook-read policy/help questions no longer fall to `active_task_context_unhandled`.
- They route to `active_task_non_mutating_language` with no plan mutation.

Not fixed / later:
- Active direct content-read safe-block families 019-023.
- Pending clarification policy behavior.
- Workbook-read preflight wording ambiguity.
- Policy visibility in `/api/plan`.
- Registry execution-disabled response-shape hardening.
