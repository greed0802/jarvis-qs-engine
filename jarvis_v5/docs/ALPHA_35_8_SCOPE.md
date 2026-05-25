# v5.0.0-alpha.35.8 — Workbook Read Policy Plan Visibility

Scope: additive workbook-read policy visibility in `/api/plan` and chat readiness.

Rules:
- No workbook read.
- No Builder engine call.
- No Excel output.
- No legacy Builder call.
- No route ownership change.
- No sheet-name probe behavior change.
- No pending clarification behavior change.
- No readiness.status override.

Added visibility:
- `workbook_read_policy.status`
- `readiness.workbook_read_policy_status`
- `readiness.workbook_read_policy_reviewed`
- `readiness.workbook_read_policy`

Main readiness status remains `contract_ready` when the contract is ready.
