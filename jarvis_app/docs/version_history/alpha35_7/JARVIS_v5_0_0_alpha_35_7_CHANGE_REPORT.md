# JARVIS v5.0.0-alpha.35.7 Change Report

## Version

v5.0.0-alpha.35.7 — Workbook Read Policy Response Contract Cleanup, no behavior change, no workbook read.

## Base used

v5.0.0-alpha.35.6 — Active-task Direct Content-read Safe-block Route Ownership, no workbook read.

## Fallback

v5.0.0-alpha.35.5.1 remains the previous fully local accepted fallback.

## Confirmed scope

1. Public future workbook-read tier labels now show current public workbook-open/read access as disabled unless explicitly enabled.
2. Workbook read preflight now separates metadata completeness from access allowed.
3. Registry requirement-check and registry endpoints now expose summary safety fields.
4. Version and test pack locks updated to v5.0.0-alpha.35.7.
5. Alpha.35.6 root reports/start files archived under `jarvis_v5/docs/version_history/alpha35_6/`.

## Runtime files changed

- `jarvis_v5/config.py`
- `jarvis_v5/tools/builder/workbook_read_policy_review.py`
- `jarvis_v5/tools/builder/workbook_read_preflight_contract.py`
- `jarvis_v5/registry/registry_loader.py`
- `jarvis_v5/schemas/message_schema.py`
- `jarvis_v5/schemas/registry_schema.py`

## Functions changed

- `FUTURE_ACCESS_TIERS` in `workbook_read_policy_review.py`
- `_workbook_preflight_metadata_validation()` in `workbook_read_preflight_contract.py`
- `evaluate_workbook_read_preflight_dry_run()` in `workbook_read_preflight_contract.py`
- `registry_safety_payload()` in `registry_loader.py`
- `_highest_risk()` added in `registry_loader.py`
- `_requires_registry_approval()` added in `registry_loader.py`
- `requirement_check()` in `registry_loader.py`
- `WorkbookReadPreflightDryRunResponse` schema
- `RegistryRequirementCheckResponse` schema

## Protected / not touched

- No route ownership change.
- No sheet-name probe behavior change.
- No pending clarification behavior change.
- No plan/readiness persistence change.
- No workbook read enabled.
- No workbook open behavior changed.
- No safe path resolver behavior changed.
- No preview policy change.
- No Builder engine / legacy Builder call.
- No Formatter / QA Checker / O&A / UI / Output Center.
- No Builder formula/export engine touched.

## Old vs new hash summary

Detailed hashes are in `JARVIS_v5_0_0_alpha_35_7_HASH_SUMMARY.json`.

## Protected Builder boundary hash result

10 / 10 protected Builder boundary files unchanged.

## Duplicate checks

- Duplicate FastAPI routes: 0
- Duplicate same-file top-level functions/classes: 0

## Package hygiene

Final package cleaned:

- `__pycache__`: 0
- `.pyc`: 0
- `.pytest_cache`: 0
- `jarvis_v5/data` non-`.keep` runtime files: 0

## Changed file inventory

See `JARVIS_v5_0_0_alpha_35_7_CHANGED_FILES.json`.
