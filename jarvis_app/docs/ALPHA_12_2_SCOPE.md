# v5.0.0-alpha.12.2 — QA Runner Report Directory + Sample Pack Assertion Fix, no engine

## Scope

- Auto-create `jarvis_v5/data/test_reports` before writing QA report JSON/Markdown files.
- Return structured `report_write_error` in the QA runner result if report writing fails.
- Keep `sample_external_ai_pack_valid` passing with `write_report=true` and `write_report=false`.
- Keep built-in `alpha11_contract_negative_guards` passing.
- Keep bad JSON and missing fixture failures structured.

## Protected systems

No Builder engine, no workbook reading/parsing, no formula generation, no Excel output, no Formatter, no QA, no O&A, no UI redesign, and no current Jarvis replacement.

## Safety locks

- workbook_read=false
- engine_called=false
- excel_created=false
- contract_only=true
- legacy_builder_called=false
