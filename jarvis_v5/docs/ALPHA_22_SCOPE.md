# v5.0.0-alpha.22.1 — QS Intent Alias Router + No-Fallback Clarification Guard, no engine

## Purpose

Improve route ownership confidence for changeable QS phrases before any Builder engine connection.

## Added

- Controlled QS Builder-start alias detector for BOQ/BQ/Bill of Quantities/Schedule of Values/Trade Schedule/Tender BOQ/NRM/SMM/regional terms.
- Negative guards for casual/non-QS phrases such as meeting schedules and definition questions.
- No-fallback clarification guard for ambiguous tool-like phrases.
- Active Builder task priority guard so QS aliases do not silently reset the current task.
- Route confidence fields on `/api/chat` responses:
  - `route_confidence`
  - `confidence_reason`
  - `tool_candidates`
  - `fallback_used`
  - `requires_clarification`

## Protected

- No Builder engine call.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter execution.
- No QA Checker execution.
- No O&A.
- No UI redesign.
- No current Jarvis replacement.

## Safety locks

All expected safety flags remain false:

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `legacy_builder_called=false`
- `contract_only=true`
