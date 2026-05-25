# Alpha 35.15 Scope — Job Center + Output Manifest Contract

Version: v5.0.0-alpha.35.15
Base: v5.0.0-alpha.35.14

This build is metadata/schema only. It defines future Job Center and Output Manifest contracts without adding workers, endpoints, output files, download routes, or runtime execution.

## Included
- `job_contract_schema.py`
- `output_manifest_schema.py`
- disabled registry metadata for future job/output management
- alpha35.15 smoke and JSON tests

## Excluded
- no worker
- no background execution
- no job store runtime
- no output files
- no download routes
- no Output Center runtime
- no workbook read
- no Builder/Formatter/QA/O&A/Document Reader execution

Safety locks remain: workbook_read=false, engine_called=false, excel_created=false, legacy_builder_called=false.
