# Jarvis v5.0.0-alpha.33 Change Report

## Base
v5.0.0-alpha.32C.1 — README / Current Package Documentation Hygiene, no behavior change, no workbook read.

## Scope
Workbook Metadata Probe Approval Contract, metadata-only, approval-gated, no workbook parsing, no Builder engine, no Excel output.

## Runtime changes
- Added `WorkbookMetadataProbeApprovalRequest` and `WorkbookMetadataProbeApprovalResponse` schemas.
- Added `jarvis_v5/tools/builder/workbook_metadata_probe_approval.py` as the single owner for metadata probe approval logic.
- Added `POST /api/builder/workbook-metadata-probe-approval` endpoint wrapper in `app.py`.
- Added QA runner endpoint/route allowlist support.
- Added alpha.33 smoke test and JSON pack.

## No behavior changes outside scope
- No workbook file open/read/parse.
- No sheet names read.
- No Builder engine call.
- No legacy Builder call.
- No Excel output.
- No router/parser behavior change.
- No Formatter/QA/O&A/UI/Output Center change.
- No registry execution flag change.

## Safety contract
Even when `approval_granted=true`, alpha.33 returns metadata only and keeps:
- workbook_opened=false
- workbook_read=false
- workbook_parsed=false
- sheet_names_read=false
- cells_read=false
- formulas_read=false
- engine_called=false
- excel_created=false
- legacy_builder_called=false
