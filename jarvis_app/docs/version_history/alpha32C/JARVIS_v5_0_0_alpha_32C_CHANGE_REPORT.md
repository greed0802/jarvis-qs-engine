# Change Report — v5.0.0-alpha.32C

## Base

v5.0.0-alpha.32A

## Scope

Cross-file Helper Duplicate Disposition Allowlist, no behavior change, no workbook read.

## Files changed

- `jarvis_v5/config.py` — version/app-name metadata only
- `jarvis_v5/docs/ALPHA_32C_SCOPE.md`
- `jarvis_v5/docs/ALPHA_32C_DUPLICATE_DISPOSITION_ALLOWLIST.md`
- `jarvis_v5/docs/PROTECTED_BUILDER_BOUNDARY_HASH_MANIFEST_ALPHA_32C.md`
- `JARVIS_v5_0_0_alpha_32C_CHANGE_REPORT.md`
- `JARVIS_v5_0_0_alpha_32C_TEST_REPORT.md`
- `JARVIS_v5_0_0_alpha_32C_TEST_RUN_RESULTS.txt`
- `JARVIS_v5_0_0_alpha_32C_DUPLICATE_SCAN_REPORT.md`
- `JARVIS_v5_0_0_alpha_32C_PACKAGE_HYGIENE_REPORT.md`
- `JARVIS_v5_0_0_alpha_32C_TARGETED_WEAKNESS_SUBSET_REPORT.md`
- `CURRENT_BACKEND_STATUS_v5_alpha_32C.md`
- `NEXT_CHAT_HANDOFF_v5_alpha_32C.md`
- `CHAT_CONTEXT_ARCHIVE_v5_alpha_32C.md`
- `alpha32C_all_pack_results.json`
- retained smoke/JSON test version metadata
- start script names updated to alpha.32C

## Functions changed

No runtime functions were changed.

## What changed

- Replaced vague duplicate wording with classified duplicate disposition.
- Documented 29 cross-file helper/function duplicates as 0 runtime-risk.
- Added watchlist owners for five runtime-adjacent helper concepts.
- Updated package metadata and test metadata to alpha.32C.
- Archived alpha.32A root artifacts into version history.

## What was not touched

- Router behavior
- Parser behavior
- Workbook read/access behavior
- Builder engine execution
- Excel output
- Formatter
- QA Checker
- O&A
- UI
- Output Center
- Registry execution flags
- Helper implementations / helper names / helper consolidation

## Safety

- WORKBOOK_READ_ENABLED remains False
- BUILDER_ENGINE_EXECUTION_ENABLED remains False
- LEGACY_BUILDER_CALLABLE remains False
- EXCEL_OUTPUT_ENABLED remains False
