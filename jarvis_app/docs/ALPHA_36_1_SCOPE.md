# Alpha 36.1 Scope — Workbook Metadata Probe Plan

Version: `v5.0.0-alpha.36.1`
Base: `v5.0.0-alpha.36.0`

Scope is metadata-only planning for a future sheet-name-only metadata probe. Alpha36.1 does not open workbooks, list sheets, import workbook readers, call the safe path resolver, add endpoints, or touch runtime tools.

Safety locks: workbook_read=false, workbook_content_read=false, sheet_name_probe_allowed=false, formula_read=false, cell_value_read=false, style_read=false, engine_called=false, excel_created=false, legacy_builder_called=false.
