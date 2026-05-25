# Jarvis v5.0.0-alpha.29 Change Report

Base: v5.0.0-alpha.28.1
Scope: Safe Workbook Path Resolver Dry Run, still no workbook open/read.

## Files changed

Runtime / schema / endpoint:

- `jarvis_v5/config.py`
- `jarvis_v5/app.py`
- `jarvis_v5/schemas/message_schema.py`
- `jarvis_v5/tools/builder/safe_workbook_path_resolver.py`

Tests / QA runner:

- `jarvis_v5/qa_runner/test_executor.py`
- `jarvis_v5/tests/smoke/test_alpha29_safe_workbook_path_resolver_dry_run.py`
- `jarvis_v5/tests/packs/alpha29_safe_workbook_path_resolver_dry_run_tests.json`
- exact version/scope assertions in existing retained tests/packs

Docs / handoff / reports:

- `README.md`
- `jarvis_v5/docs/JARVIS_PATCH_GOVERNANCE_RULES.md`
- `jarvis_v5/docs/ALPHA_29_SCOPE.md`
- `jarvis_v5/docs/DORMANT_CODE_REGISTRY_ALPHA_29.md`
- `jarvis_v5/docs/SAFE_WORKBOOK_PATH_RESOLVER_DRY_RUN_ALPHA_29.md`
- `jarvis_v5/docs/PROTECTED_BUILDER_BOUNDARY_HASH_MANIFEST_ALPHA_29.md`
- `CURRENT_BACKEND_STATUS_v5_alpha_29.md`
- `NEXT_CHAT_HANDOFF_v5_alpha_29.md`
- `CHAT_CONTEXT_ARCHIVE_v5_alpha_29.md`

## What changed

- Added dedicated metadata-only Safe Workbook Path Resolver Dry Run owner.
- Added `POST /api/builder/safe-workbook-path-resolver-dry-run`.
- Added request/response schemas for resolver dry run.
- Added raw path scrub tests proving internal `saved_path` is not returned by the resolver response.
- Added dormant-code registry and preservation rule.
- Added package cleanup/version tag hygiene rule.
- Archived alpha.28.1 root artifacts under `jarvis_v5/docs/version_history/alpha28_1/`.

## What was not touched

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

## Safety

No workbook path was resolved, no filesystem check was performed, no workbook was opened/read, no Builder engine was called, no legacy Builder was called, and no Excel output was created.
