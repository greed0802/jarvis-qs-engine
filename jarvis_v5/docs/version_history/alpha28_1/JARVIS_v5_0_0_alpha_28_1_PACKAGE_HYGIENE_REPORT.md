# Package Hygiene Report — v5.0.0-alpha.28.1

Scope: Package Artifact Deduplication + Helper Duplicate Audit, no behavior change.

## Package root before cleanup

Alpha.28 root contained stale alpha.27 release artifacts plus alpha.28 release artifacts.

Known stale alpha.27 root artifacts from Batch 0:

```text
CURRENT_BACKEND_STATUS_v5_alpha_27.md
NEXT_CHAT_HANDOFF_v5_alpha_27.md
START_JARVIS_V5_ALPHA_27.bat
START_JARVIS_V5_ALPHA_27_SIMPLE_NO_RELOAD.bat
JARVIS_v5_0_0_alpha_27_CHANGE_REPORT.md
JARVIS_v5_0_0_alpha_27_TEST_REPORT.md
JARVIS_v5_0_0_alpha_27_TEST_RUN_RESULTS.txt
alpha27_all_pack_results.json
```

Known alpha.28 root release artifacts archived for alpha.28.1:

```text
CHAT_CONTEXT_ARCHIVE_v5_alpha_28.md
CURRENT_BACKEND_STATUS_v5_alpha_28.md
NEXT_CHAT_HANDOFF_v5_alpha_28.md
JARVIS_v5_0_0_alpha_28_CHANGE_REPORT.md
JARVIS_v5_0_0_alpha_28_TEST_REPORT.md
JARVIS_v5_0_0_alpha_28_TEST_RUN_RESULTS.txt
alpha28_all_pack_results.json
```

## Package root after cleanup

Current alpha.28.1 root files:

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

## Intentionally kept in root

- alpha.28.1 reports and status/handoff files
- alpha.28.1 pack results
- alpha.28.1 start scripts
- README/current docs
- source package files

## Intentionally excluded from root

- alpha.27 root release artifacts
- alpha.28 root release artifacts
- old alpha.27/alpha.28 BAT launchers
- `__pycache__`, `.pytest_cache`, and `.pyc` files from final package

## Confirmation

No stale alpha.27 or alpha.28 root release artifacts remain after cleanup. Final ZIP inventory check passed after packaging.
