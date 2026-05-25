# Alpha 36.3 Scope — Controlled Sheet-name-only Probe Implementation Plan

Version: v5.0.0-alpha.36.3
Base: v5.0.0-alpha.36.2

Scope: planning/evidence only. This build defines the future implementation blueprint for a sheet-name-only metadata probe. It does not implement the probe.

Hard locks:

- metadata_only=true
- execution_enabled=false
- workbook_read=false
- workbook_content_read=false
- sheet_name_probe_allowed=false
- formula_read=false
- cell_value_read=false
- style_read=false
- engine_called=false
- excel_created=false
- legacy_builder_called=false
- tool_execution_called=false

Not included:

- no endpoint
- no workbook reader runtime
- no permission store runtime
- no sheet-name probe
- no worker/job/output runtime
- no safe path resolver call
- no openpyxl/pandas import for workbook reading
- no Builder/Formatter/QA/O&A/Document Reader/Output Center runtime changes
