# Jarvis v5.0.0-alpha.22.2F Scope

Engineering Language Gate + Active Non-Mutating Route Contract Cleanup, no engine.

## Added

- EngineeringLanguageGate classifier only.
- Active-task engineering explanations route as `active_task_non_mutating_language`.
- No-active-task engineering help routes through `NoActiveTaskLanguageGate` with `fallback_used=false`.
- Engineering choose-tool ambiguity routes to `choose_tool` clarification only, with no execution.
- Canonical unit evidence in reducer normalization.
- Expanded engineering term families for civil, structural, concrete, steel, reinforcement, geotech, hydraulic, pavement, drainage, survey/tolerance, temporary works, sustainability, report/code, and unit language.

## Protected

- No Builder engine.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter.
- No QA Checker.
- No O&A.
- No snapshot/adapter/contract/preflight/execution logic changes.
- No UI redesign.
