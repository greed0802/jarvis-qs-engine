# Advisory Route Contract — Alpha35.13 Evidence Lock

## Route family

Top-level route remains:

```text
registry_advisory_metadata_only
```

No new route family is introduced by alpha35.13.

## Advisory types carried by the existing route

- `capability_advisory`
- `qs_scope_advisory`
- `file_requirement_advisory`
- `rfi_template_advisory`
- `scope_risk_advisory`

## Required safety fields

Advisory responses must remain metadata-only:

```text
metadata_only=true
execution_enabled=false
tool_execution_called=false
workbook_read=false
engine_called=false
excel_created=false
legacy_builder_called=false
```

## Future-tool execution wording

When a user asks to run a future tool, Jarvis may acknowledge the capability request but must not execute it.

Expected metadata:

```text
future_tool_requested=true
execution_requested=true
execution_blocked=true
blocked_reason=future_tool_execution_disabled
```

## Unknown scope wording

Unknown scope/trade advisory requests should clarify instead of guessing.

Expected metadata:

```text
known_scope=false
unknown_scope=true
requires_clarification=true
```

## Explicit exclusions

- No active-task advisory in alpha35.13
- No Builder mutation
- No workbook read
- No Formatter/QA/O&A execution
- No Output Center changes
