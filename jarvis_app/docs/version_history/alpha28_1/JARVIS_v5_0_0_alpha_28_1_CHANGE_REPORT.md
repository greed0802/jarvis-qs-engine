# Jarvis v5.0.0-alpha.28.1 Change Report

## Version

`v5.0.0-alpha.28.1`

## Base version

`v5.0.0-alpha.28`

## Scope

Package Artifact Deduplication + Helper Duplicate Audit, no behavior change.

## Files changed

- `jarvis_v5/config.py` — version/name metadata only.
- `README.md` — current package summary.
- `START_JARVIS_V5_ALPHA_28_1.bat` — current launch script.
- `START_JARVIS_V5_ALPHA_28_1_SIMPLE_NO_RELOAD.bat` — current launch script.
- `jarvis_v5/docs/version_history/alpha27/*` — archived alpha.27 root artifacts.
- `jarvis_v5/docs/version_history/alpha28/*` — archived alpha.28 root artifacts.
- `jarvis_v5/docs/DUPLICATE_SCAN_REPORT_ALPHA_28_1.md`.
- `jarvis_v5/docs/PACKAGE_HYGIENE_ALPHA_28_1.md`.
- `JARVIS_v5_0_0_alpha_28_1_DUPLICATE_SCAN_REPORT.md`.
- `JARVIS_v5_0_0_alpha_28_1_PACKAGE_HYGIENE_REPORT.md`.
- `jarvis_v5/tests/smoke/test_alpha28_1_package_hygiene.py`.
- `jarvis_v5/tests/packs/alpha28_1_package_hygiene_tests.json`.
- Existing smoke tests and JSON packs: exact version assertions updated from alpha.28 to alpha.28.1 only.

## Runtime behavior

No runtime behavior was changed. Preview policy response behavior, schema behavior, router behavior, Builder engine boundaries, workbook read, Excel output, Formatter, QA, O&A, UI, and Output Center were not changed.

## Safety locks

All execution safety locks remain false.

## Package root after cleanup

```text
CHAT_CONTEXT_ARCHIVE_v5_alpha_28_1.md
CURRENT_BACKEND_STATUS_v5_alpha_28_1.md
JARVIS_v5_0_0_alpha_28_1_CHANGE_REPORT.md
JARVIS_v5_0_0_alpha_28_1_DUPLICATE_SCAN_REPORT.md
JARVIS_v5_0_0_alpha_28_1_PACKAGE_HYGIENE_REPORT.md
JARVIS_v5_0_0_alpha_28_1_TEST_REPORT.md
JARVIS_v5_0_0_alpha_28_1_TEST_RUN_RESULTS.txt
NEXT_CHAT_HANDOFF_v5_alpha_28_1.md
README.md
START_JARVIS_V5_ALPHA_28_1.bat
START_JARVIS_V5_ALPHA_28_1_SIMPLE_NO_RELOAD.bat
alpha28_1_all_pack_results.json
conftest.py
requirements.txt
run_alpha_smoke_tests.py
```

## Archived alpha.27 artifacts

```text
CURRENT_BACKEND_STATUS_v5_alpha_27.md
JARVIS_v5_0_0_alpha_27_CHANGE_REPORT.md
JARVIS_v5_0_0_alpha_27_TEST_REPORT.md
JARVIS_v5_0_0_alpha_27_TEST_RUN_RESULTS.txt
NEXT_CHAT_HANDOFF_v5_alpha_27.md
START_JARVIS_V5_ALPHA_27.bat
START_JARVIS_V5_ALPHA_27_SIMPLE_NO_RELOAD.bat
alpha27_all_pack_results.json
```

## Archived alpha.28 artifacts

```text
CHAT_CONTEXT_ARCHIVE_v5_alpha_28.md
CURRENT_BACKEND_STATUS_v5_alpha_28.md
JARVIS_v5_0_0_alpha_28_CHANGE_REPORT.md
JARVIS_v5_0_0_alpha_28_TEST_REPORT.md
JARVIS_v5_0_0_alpha_28_TEST_RUN_RESULTS.txt
NEXT_CHAT_HANDOFF_v5_alpha_28.md
alpha28_all_pack_results.json
```

## Final tests

- compileall: PASS
- pytest: PASS — 225 passed
- JSON packs: PASS — 27 / 27
- JSON pack tests: PASS — 116 / 116
- safety aggregate: all false
- duplicate FastAPI routes: 0
- same-file duplicate top-level definitions: 0
- protected Builder boundary hash check: 10 / 10 unchanged
