# Alpha36.2 Scope — Sheet-name-only Metadata Probe Dry Run

Version: `v5.0.0-alpha.36.3`
Base: `v5.0.0-alpha.36.1`

Scope: diagnostic/evidence only. No implementation.

Hard locks:
- `metadata_only=true`
- `execution_enabled=false`
- `workbook_read=false`
- `workbook_content_read=false`
- `sheet_name_probe_allowed=false`
- `formula_read=false`
- `cell_value_read=false`
- `style_read=false`
- `engine_called=false`
- `excel_created=false`
- `legacy_builder_called=false`

Alpha36.2 documents future patch positions for a sheet-name-only probe. It does not open, parse, probe, or inspect workbooks.
