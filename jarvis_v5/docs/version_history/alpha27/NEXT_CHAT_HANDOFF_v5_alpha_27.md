# Next Chat Handoff — v5.0.0-alpha.27

## Current version
v5.0.0-alpha.27 — Workbook Access Boundary + Preview Execution Policy, still no workbook read.

## Base used
v5.0.0-alpha.26.1 — Response Schema + Test Pack Hygiene Cleanup, no behavior change.

## What changed
- Added metadata-only preview execution policy owner.
- Added endpoint `POST /api/builder/preview-execution-policy`.
- Added policy/docs for workbook read boundary, path resolver, preview/export approval, preview result schema, output manifest schema, background jobs, Formula Integrity Guard connection, and failure recovery.
- Added alpha.27 smoke and JSON pack tests.

## Safety
All retained no-engine safety locks must remain false:
- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## Next recommended step
Diagnose alpha.27 package/report correctness, then decide whether to keep alpha.27 as policy checkpoint or proceed to alpha.28 dry run. Do not enable workbook reading yet.
