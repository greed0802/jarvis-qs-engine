# v5.0.0-alpha.7 — Builder Setup Completeness Gate, no engine

## Scope

Add a setup completeness validator and display missing Builder slots in:

- `/api/plan/{conversation_id}`
- Review response
- BuilderRunSnapshot response and model
- Builder Adapter Dry Run response and input
- Preview/Export safe stubs

## Builder slots checked

- workbook_ref
- trade_profile
- costx_function
- custom_quantity when `XGETCUSTOM`
- unit
- dynamic_zones for rebuild mode
- heading_assignments for rebuild mode
- levels unless preserve-source count mode applies
- pending clarification
- current snapshot / current adapter freshness when applicable

## Explicitly not connected

- No Builder engine
- No workbook reading/parsing
- No sheet inspection
- No formula generation
- No Excel output
- No Formatter
- No QA Checker
- No O&A
- No UI redesign
- No current Jarvis replacement

## Safety proof fields

```text
workbook_read = false
engine_called = false
excel_created = false
```
