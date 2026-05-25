# v5.0.0-alpha.17 — Legacy Builder Engine Bridge Stub + Execution Kill Switch, no workbook read

Alpha.17 adds a non-executing legacy Builder bridge stub and a hard execution kill switch.

## Scope

- Add `POST /api/builder/engine-execution-request`.
- Validate latest contract and latest preflight before a future execution path.
- Always block execution while the kill switch is off.
- Expose execution lock status in `/api/version`, `/api/plan`, and Review.
- Add imported QA pack support for the execution-request endpoint.

## Safety locks

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `contract_only=true`
- `legacy_builder_called=false`

## Explicitly out of scope

- No Builder engine call.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter.
- No QA logic.
- No O&A.
- No UI redesign.
- No current Jarvis replacement.
