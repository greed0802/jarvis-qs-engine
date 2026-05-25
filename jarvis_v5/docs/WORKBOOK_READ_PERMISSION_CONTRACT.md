# Workbook Read Permission Contract

Alpha35.18 defines permission contracts only. It does not grant or perform workbook access.

## Contract objects

- `permission_request_id`
- user approval state
- allowed file reference
- allowed sheet scope
- allowed range scope
- metadata-only permission
- content-read permission placeholder
- revocation state
- expiry state
- audit event contract
- safety envelope
- blocked read reasons

## Default safety

All defaults are no-read and no-execution:

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
tool_execution_called=false
```

## Future approval states

- `not_requested`
- `requires_approval`
- `approved_metadata_only`
- `approved_sheet_name_probe`
- `approved_content_read`
- `rejected`
- `revoked`
- `expired`

Alpha35.18 does not persist or enforce these states at runtime. They are schema metadata only.

## Blocked read reasons

- `permission_not_requested`
- `approval_required`
- `approval_rejected`
- `permission_revoked`
- `permission_expired`
- `file_ref_missing`
- `sheet_scope_missing`
- `range_scope_missing`
- `sheet_name_probe_not_approved`
- `content_read_not_approved`
- `formula_read_not_approved`
- `cell_value_read_not_approved`
- `workbook_read_disabled`
- `execution_disabled`
