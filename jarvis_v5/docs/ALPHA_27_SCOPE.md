# v5.0.0-alpha.27 Scope

## Title
Workbook Access Boundary + Preview Execution Policy, still no workbook read

## Purpose
Alpha.27 defines the policy gates required before any future workbook read, preview execution, export execution, output manifest creation, background job execution, or Formula Integrity Guard connection.

This build is still metadata-only. It does not perform preview/export execution.

## Added
- Workbook read permission boundary policy.
- Safe workbook path resolver policy.
- Preview-only approval policy.
- Export approval policy.
- Preview result schema definition.
- Output manifest schema definition.
- Background job boundary plan.
- Formula Integrity Guard connection point definition.
- Legacy Builder failure recovery contract.
- Metadata-only endpoint: `POST /api/builder/preview-execution-policy`.

## Safety locks
- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `legacy_builder_called=false`
- `execution_enabled=false`

## Out of scope
- Workbook reading/parsing.
- Legacy Builder import/call.
- Formula generation.
- Preview row creation.
- Excel output.
- Formatter, QA Checker, O&A.
- Route behavior changes.
- UI redesign.
