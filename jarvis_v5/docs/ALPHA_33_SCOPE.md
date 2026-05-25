# v5.0.0-alpha.33 — Workbook Metadata Probe Approval Contract

Version: v5.0.0-alpha.33
Base: v5.0.0-alpha.32C.1

Scope:
- Add a user-facing workbook metadata probe approval contract.
- Metadata-only and approval-gated.
- No workbook opening, parsing, sheet-name reading, cell reading, formula reading, Builder engine call, legacy Builder call, or Excel output.

New endpoint:
- `POST /api/builder/workbook-metadata-probe-approval`

New owner:
- `jarvis_v5/tools/builder/workbook_metadata_probe_approval.py`

Allowed metadata:
- workbook_id
- attachment_id
- filename
- extension
- content_type
- size_bytes
- source
- conversation_id
- contract_id
- workbook_ref_found
- metadata_validation result

Blocked in alpha.33:
- sheet names
- workbook dimensions
- cell values
- formulas
- workbook parse result
- raw local path
- preview/export readiness upgrade

Governance:
- `app.py` only exposes the endpoint wrapper.
- No router/parser behavior change.
- No existing safe workbook path resolver behavior change.
- No existing workbook read preflight behavior change.
- No existing preview execution policy behavior change.
