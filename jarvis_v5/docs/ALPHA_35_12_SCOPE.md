# Alpha 35.12 Scope — Advisory Route Precision + Future Tool Clarification Contract

Version: `v5.0.0-alpha.35.12`

Base: `v5.0.0-alpha.35.11 — Metadata-only Capability Advisory + QS Scope/RFI Advisor, no execution`

## Purpose

Alpha35.12 hardens the metadata-only advisory lane added in alpha35.11.

It adds:

1. Future-tool execution-request metadata:
   - `future_tool_requested`
   - `execution_requested`
   - `execution_blocked`
   - `blocked_reason = future_tool_execution_disabled`

2. Unknown QS scope clarification metadata:
   - `known_scope`
   - `unknown_scope`
   - `clarification_questions`

3. Narrow no-active advisory route precision for direct future-tool comparison/execution prompts.

4. Advisory regression pack coverage.

## Safety boundary

Still locked:

```text
workbook_read=false
engine_called=false
excel_created=false
legacy_builder_called=false
```

No tool execution was added.

## Explicitly not included

```text
No active-task advisory route
No Builder mutation
No Builder engine
No workbook content read/parse
No Excel output
No Formatter execution
No QA Checker execution
No O&A execution
No UI change
No Output Center change
No preview policy change
No safe path resolver change
No workbook policy runtime change
```

## Route ownership

```text
No-active advisory route owner:
jarvis_v5/router/no_active_task_language_gate.py

Metadata advisory contract owner:
jarvis_v5/registry/registry_loader.py

Response schema owner:
jarvis_v5/schemas/registry_schema.py
```

`main_router.py` was not changed. Existing `registry_advisory_metadata_only` carries the new metadata.
