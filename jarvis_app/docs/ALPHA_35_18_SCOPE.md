# Alpha35.18 Scope — Workbook Read Permission Contract

Version: `v5.0.0-alpha.35.18`
Base: `v5.0.0-alpha.35.17`

## Scope

Metadata-only workbook read permission contract.

## Allowed

- Define workbook permission request schema.
- Define approval, sheet scope, range scope, revocation, expiry, audit, and blocked reason contracts.
- Add registry metadata describing future workbook permission requirements.
- Add tests and documentation.

## Not allowed

- No workbook read.
- No workbook content read.
- No sheet-name probe.
- No formula read.
- No cell value read.
- No workbook reader runtime.
- No permission store runtime.
- No endpoint.
- No Builder engine.
- No Excel output.
- No route behavior change.

## Safety locks

```text
metadata_only=true
execution_enabled=false
workbook_read=false
workbook_content_read=false
formula_read=false
cell_value_read=false
sheet_name_probe_allowed=false
engine_called=false
excel_created=false
legacy_builder_called=false
```
