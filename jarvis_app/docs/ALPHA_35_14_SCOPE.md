# v5.0.0-alpha.35.14 — Formatter / QA / O&A / Bulkcheck / Document Reader Contract Map

Scope: metadata-only future tool contract map.

This build defines future tool contract metadata for Formatter, QA Checker, O&A Delta Builder, Bulkcheck Helper, BOQ Compare, Description / BOQ Writer, Document Reader, Standards KB, and Output Center.

No execution is enabled. No workbook content is read. No Builder engine is connected. No Excel output is created.

## Safety locks

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `legacy_builder_called=false`

## Runtime behavior

No route behavior was changed. No new endpoint was added. The contract map is registry/schema metadata only.
