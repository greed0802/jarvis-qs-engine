# v5.0.0-alpha.20 — Legacy Builder Import Boundary Audit, no call

## Base

v5.0.0-alpha.19 — Contract Fixture Replay + Golden Diff Tests, no engine.

## Purpose

Alpha.20 adds a no-call Legacy Builder import boundary audit and cleans stale alpha.11 wording from runtime stub messages.

## Added

- `POST /api/builder/legacy-import-boundary-audit`
- `GET /api/builder/legacy-import-boundary-audit/latest/{conversation_id}`
- Static no-call import boundary report
- `/api/plan` visibility for latest legacy import boundary audit
- QA runner support for the new audit endpoint and route
- Alpha.20 smoke tests and JSON pack

## Cleanup included

Runtime stub messages now use `APP_VERSION` instead of stale `alpha.11` wording.

## Safety boundary

Alpha.20 does not import or call the legacy Builder runtime.

Hard locks stay closed:

```text
workbook_read=false
engine_called=false
excel_created=false
contract_only=true
legacy_builder_called=false
```

## Protected systems

Not touched:

```text
Builder engine
Legacy Builder import/call
Workbook reading/parsing
CostX formula generation
Formula Integrity Guard
Excel output
Formatter
QA Checker
O&A
UI redesign
Current Jarvis replacement
```
