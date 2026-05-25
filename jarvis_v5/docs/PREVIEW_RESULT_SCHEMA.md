# Builder Preview Result Schema — v1

Alpha.27 defines this schema only. It does not emit engine-generated preview rows.

Required future fields:
- `preview_id`
- `conversation_id`
- `contract_id`
- `source_workbook_ref`
- `preview_status`
- `row_count`
- `zone_summary`
- `level_summary`
- `formula_integrity_status`
- `safety`

Safety defaults:
- `workbook_read=false` until future read-enabled alpha.
- `engine_called=false` until future execution-enabled alpha.
- `excel_created=false` until future export-enabled alpha.
- `legacy_builder_called=false` until future bridge-enabled alpha.
