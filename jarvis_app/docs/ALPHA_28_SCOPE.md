# v5.0.0-alpha.28 Scope

## Title
Policy Response Hygiene + Approval Token Readiness Contract, still no workbook read

## Base
v5.0.0-alpha.27 — Workbook Access Boundary + Preview Execution Policy, still no workbook read

## Purpose
Alpha.28 tightens the metadata-only preview/export policy response before any future workbook access or Builder execution. It adds permanent patch governance rules, a safe chat-context archive for handoff continuity, a public/scrubbed contract summary, and machine-readable approval readiness objects.

## Included
1. Permanent Jarvis patch governance Markdown.
2. Chat-context archive Markdown for zero-practical-context-loss handoff.
3. Version and documentation hygiene updates.
4. Public `contract_summary` on `/api/builder/preview-execution-policy`.
5. Normal policy responses return `contract = null` instead of raw stored contract payload.
6. Approval token policy schema, defined only and not issued.
7. Preview approval readiness object.
8. Export approval readiness object.
9. Blocked reason detail normalization.
10. Alpha.28 smoke tests and JSON pack coverage.

## Safety locks
- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `legacy_builder_called=false`
- `execution_enabled=false`

## Out of scope
- Workbook reading/parsing.
- Legacy Builder import/call.
- Builder engine execution.
- Formula generation.
- Preview row creation.
- Excel output.
- Formatter, QA Checker, O&A.
- Router/reducer/parser behavior changes.
- UI redesign.
- Background jobs.
