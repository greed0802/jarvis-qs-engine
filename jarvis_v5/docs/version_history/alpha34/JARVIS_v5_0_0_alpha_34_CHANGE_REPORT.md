# JARVIS v5.0.0-alpha.34 Change Report

## Version

v5.0.0-alpha.34 — Sheet Name Probe Approval Contract.

## Base

v5.0.0-alpha.33.2 — Release Artifact Test Version Hygiene.

## Scope

Added a separate approval-gated sheet-name probe boundary. The probe may open an uploaded workbook in read-only mode only after explicit approval and returns sheet names/sheet count only.

## Runtime owner added

- `jarvis_v5/tools/builder/workbook_sheet_name_probe_approval.py`

## Endpoint added

- `POST /api/builder/workbook-sheet-name-probe-approval`

## Not changed

Router behavior, parser behavior, safe workbook path resolver behavior, workbook read preflight behavior, preview execution policy behavior, Builder engine, Formatter, QA, O&A, UI, Output Center, and registry execution flags were not changed.
