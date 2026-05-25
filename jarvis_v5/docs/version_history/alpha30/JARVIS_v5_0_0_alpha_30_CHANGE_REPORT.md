# Jarvis v5.0.0-alpha.30 Change Report

## Version

v5.0.0-alpha.30

## Base

v5.0.0-alpha.29

## Scope

Workbook Read Preflight Contract, still no workbook parse/output.

## Added

- `jarvis_v5/tools/builder/workbook_read_preflight_contract.py`
- `POST /api/builder/workbook-read-preflight-dry-run`
- `WorkbookReadPreflightDryRunRequest`
- `WorkbookReadPreflightDryRunResponse`
- Alpha.30 smoke tests and JSON pack
- Alpha.30 scope and preflight documentation

## Changed

- Updated app version/scope metadata to alpha.30.
- Added endpoint exposure in `app.py` only.
- Added QA runner endpoint/route allowlist compatibility.
- Archived alpha.29 root release artifacts under `jarvis_v5/docs/version_history/alpha29/`.

## Not touched

- Builder formula/export engine
- CostX formula generation
- Formula Integrity Guard execution
- legacy Builder execution bridge
- workbook reader/parser
- Excel output writer
- router core
- slot reducer
- Builder parser
- Formatter
- QA Checker
- O&A
- UI
- Output Center
- background jobs
- preview execution policy behavior

## Execution status

Workbook read, workbook parse, Builder engine execution, legacy Builder callable, and Excel output remain disabled.
