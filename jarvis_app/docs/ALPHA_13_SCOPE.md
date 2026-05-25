# v5.0.0-alpha.13 — Engine Boundary Audit + Contract-to-Legacy Mapping, no engine

Alpha.13 adds a no-engine audit layer for saved Builder engine contracts.

## Scope

- Add contract schema versioning.
- Add legacy Builder target metadata.
- Add a boundary audit endpoint.
- Map contract fields to the future legacy Builder input names.
- Report missing/ambiguous fields before any engine connection.
- Surface latest audit status in `/api/plan` and contract replay responses.

## Safety boundary

Alpha.13 must keep:

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `contract_only=true`
- `legacy_builder_called=false`

## Not included

- No Builder engine.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter.
- No QA.
- No O&A.
- No UI redesign.
- No current Jarvis replacement.
