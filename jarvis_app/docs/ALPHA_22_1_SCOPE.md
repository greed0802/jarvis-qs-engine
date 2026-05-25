# v5.0.0-alpha.22.1 — No-Fallback Router Tightening + Trade Ambiguity Guard, no engine

## Base

v5.0.0-alpha.22 — QS Intent Alias Router + No-Fallback Clarification Guard, no engine.

## Scope

This patch tightens router behavior found by the alpha.22 senior QS 1000-test pack.

Included:

1. Generic tool-like phrases route to `choose_tool`, not `general_stub`:
   - Compare
   - Check
   - Create
   - Run it
   - Start the tool
2. Writing-format phrases route to general writing help, not Formatter and not fallback:
   - Format this sentence
   - Format this chat reply only
3. Ambiguous low-risk trade choices clarify instead of silently choosing the first match:
   - Use Carpet or Tiling
4. Controlled QS alias added:
   - trade measure schedule
5. `route_confidence`, `confidence_reason`, `tool_candidates`, `fallback_used`, and `requires_clarification` remain exposed in `/api/chat` responses.

## Safety locks

The following remain hard locked:

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `contract_only=true`
- `legacy_builder_called=false`

## Explicitly not included

- No Builder engine.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter execution.
- No QA Checker execution.
- No O&A.
- No UI redesign.
- No current Jarvis replacement.
