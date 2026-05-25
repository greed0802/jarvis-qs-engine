# Route Contracts — v5.0.0-alpha.35.13

## registry_advisory_metadata_only

Purpose: metadata-only capability, scope, file, RFI, and future-tool advisory.

Required guarantees:

```text
metadata_only=true
execution_enabled=false
tool_execution_called=false
workbook_read=false
engine_called=false
excel_created=false
legacy_builder_called=false
```

No Builder mutation is allowed.

## active_task_preview_stub

Purpose: Preview request acknowledgement while engine remains disconnected.

Required guarantees:

```text
blocked=true or stubbed=true
workbook_read=false
engine_called=false
excel_created=false
legacy_builder_called=false
```

## workbook-read safe blocks

Direct workbook content read, parse, inspect, formulas, cells, or sheet probe requests must stay policy-gated and must not read workbook content.

## future-tool run requests

Requests such as `Run O&A`, `Run Formatter`, `Run QA Checker`, or `Run Document Reader` must remain metadata-only/blocked unless a future approved tool contract and execution gate exists.

## Builder setup edits

Builder setup edits remain owned by the slot reducer. Advisory route changes must not consume Builder setup commands.
