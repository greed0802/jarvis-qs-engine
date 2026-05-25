# Jarvis v5.0.0-alpha.33 Bug Report

## Target issue
Missing user-facing approval contract for workbook metadata probing.

## Expected behavior
Jarvis should explain metadata-only probing, require explicit approval by default, and prove no workbook open/read/parse occurs.

## Actual previous behavior
alpha.32C.1 had safe workbook path resolver and workbook read preflight dry-run endpoints, but no dedicated metadata-probe approval lifecycle.

## Root cause
No single owner existed for metadata probe approval. Existing workbook-boundary modules were preflight/policy oriented, not a user-facing approval contract.

## Fix
Added a narrow owner module and endpoint:
- `jarvis_v5/tools/builder/workbook_metadata_probe_approval.py`
- `POST /api/builder/workbook-metadata-probe-approval`

## Result
The metadata probe approval contract is present and remains metadata-only. No workbook content access or engine execution was enabled.
