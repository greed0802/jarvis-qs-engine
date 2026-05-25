# Alpha 35.11 Scope — Metadata-only Capability Advisory + QS Scope/RFI Advisor

Version: `v5.0.0-alpha.35.11`
Base: `v5.0.0-alpha.35.10.2`

## Purpose

Add metadata-only advisory coverage for future-tool/capability guidance and QS scope/RFI helper prompts without enabling any execution path.

## Included

- Registry metadata enrichment for:
  - future-tool advisory
  - capability clarification
  - QS scope advisor
  - file requirement advisor
  - RFI template advisor
  - scope-risk checklist
- `requirement_check()` advisory response contract fields:
  - `capability_advisory`
  - `qs_scope_advisory`
  - `file_requirement_advisory`
  - `rfi_template_advisory`
  - `scope_risk_advisory`
- Narrow no-active advisory phrase ownership for:
  - “what should I measure for …”
  - “what files do I need for …”
  - “what RFI should I ask/raise …”
  - “which tool/capability should handle …”
- Alpha35.11 smoke test and JSON pack.

## Excluded

- No active-task advisory route.
- No Builder mutation.
- No workbook content read/parse.
- No Builder engine.
- No legacy Builder import/call.
- No Excel output.
- No Formatter, QA Checker, O&A, UI, Output Center, or preview policy changes.
- No registry execution flag changed to true.

## Safety lock

Expected safety fields remain:

```text
workbook_read=false
engine_called=false
excel_created=false
legacy_builder_called=false
```
