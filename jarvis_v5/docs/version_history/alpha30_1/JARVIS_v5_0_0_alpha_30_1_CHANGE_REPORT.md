# Jarvis v5.0.0-alpha.30.1 Change Report

## Version

v5.0.0-alpha.30.1

## Base

v5.0.0-alpha.30 — Workbook Read Preflight Contract, still no workbook parse/output.

## Scope

Weakness Pack Triage + Route/Response Compatibility Plan, no behavior change.

## Batches completed

- Batch 0 — baseline lock: passed
- Batch 1 — version/docs only: completed
- Batch 2 — weakness triage docs only: completed
- Batch 3 — reduced weakness-regression artifact only: completed
- Batch 4 — future patch sequence docs only: completed
- Batch 5 — reports/handoff only: completed
- Batch 6 — package cleanup before ZIP: completed
- Batch 7 — final regression/package: completed

## Files changed

Runtime metadata only:

- `jarvis_v5/config.py`
- `jarvis_v5/app.py` (`/api/version` metadata scope only)

Tests / triage artifact:

- `jarvis_v5/tests/smoke/test_alpha28_1_package_hygiene.py`
- `jarvis_v5/tests/packs/alpha30_1_weakness_triage_reduced_regression_tests.json`

Docs / reports / handoff:

- `README.md`
- `jarvis_v5/docs/ALPHA_30_1_SCOPE.md`
- `jarvis_v5/docs/WEAKNESS_8000_TRIAGE_ALPHA_30_1.md`
- `jarvis_v5/docs/WEAKNESS_PATCH_SEQUENCE_ALPHA_30_1.md`
- `jarvis_v5/docs/ROUTE_RESPONSE_COMPATIBILITY_PATCH_PLAN_ALPHA_30_1.md`
- `jarvis_v5/docs/PROTECTED_BUILDER_BOUNDARY_HASH_MANIFEST_ALPHA_30_1.md`
- `CURRENT_BACKEND_STATUS_v5_alpha_30_1.md`
- `NEXT_CHAT_HANDOFF_v5_alpha_30_1.md`
- `CHAT_CONTEXT_ARCHIVE_v5_alpha_30_1.md`
- release reports and package hygiene outputs

## What changed

- Preserved the 8,000-test weakness result as first-class triage documentation.
- Classified failures into route hygiene, response-shape compatibility, parser-sensitive risk, and future expectation groups.
- Added a pass-safe reduced weakness triage pack.
- Added future patch sequence: alpha.31A response compatibility, alpha.31B no-active route hygiene, alpha.31C active non-mutating/feedback ownership, alpha.31D clarification action coverage, alpha.31E/32 parser conflict aliases.
- Archived alpha.30 root artifacts under `jarvis_v5/docs/version_history/alpha30/`.

## What did not change

No runtime route behavior, parser behavior, Builder policy behavior, workbook preflight behavior, workbook read, Builder engine call, legacy Builder call, Excel output, Formatter, QA, O&A, UI, or Output Center behavior was changed.
