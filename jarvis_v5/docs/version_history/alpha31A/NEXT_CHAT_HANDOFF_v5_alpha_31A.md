# Next Chat Handoff — v5.0.0-alpha.31B

## Version
v5.0.0-alpha.31B

## Base
v5.0.0-alpha.30.1

## Scope
Response-shape compatibility only. No router behavior change, no parser behavior change, no workbook read.

## Added response aliases
- `/api/plan`: `version`, `latest_snapshot`, `latest_adapter`, `latest_engine_contract`.
- preview/export policy: `workbook_read_permission_boundary.workbook_read_enabled=false`.
- `/api/chat`: deterministic `plan_mutated` field while preserving true mutations.

## Deferred next work
- alpha.31B — no-active generic ambiguity / prompt-injection route hygiene.
- alpha.31C — active non-mutating + feedback read-only ownership.
- alpha.31D — pending clarification risky-action phrase coverage.
- alpha.31E/alpha.32 — parser function/unit conflict alias consolidation.

## Must not do next
Do not enable workbook read or Builder execution. Do not combine router/parser fixes with response-shape compatibility.
