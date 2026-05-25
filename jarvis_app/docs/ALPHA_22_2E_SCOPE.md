# v5.0.0-alpha.22.2E — Active Task Non-Mutating Language Gate + Plan Response Shape Cleanup, no engine

Base: v5.0.0-alpha.22.2D.

Scope:
- Add one ActiveTaskNonMutatingLanguageGate for active Builder greetings, writing help, casual help, CostX/QS explanations, and other non-mutating text.
- Keep active setup edits owned by slot_reducer only.
- Keep confidence_engine.control_taken=false for active task paths.
- Add additive active_task wrapper to /api/plan while preserving existing top-level fields.
- Update /api/version scope metadata.
- Add missing route names to QA runner known routes only.
- Fix central unit aliases for sq. m and m² without broad token-detector refactor.

Protected:
- No Builder engine.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter, QA Checker, O&A.
- No snapshot/adapter/contract/preflight/execution logic changes.
- No UI redesign.
