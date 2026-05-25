# JARVIS v5.0.0-alpha.35.5 Change Report

Version: v5.0.0-alpha.35.5
Base: v5.0.0-alpha.35.3 candidate
Scope: Windows Test Report Directory Cleanup Hygiene, test-only, no runtime behavior change, no workbook read.

Changed files:
- jarvis_v5/tests/smoke/test_cleanup.py
- jarvis_v5/tests/smoke/test_alpha12_2_report_dir_sample_pack.py
- jarvis_v5/tests/smoke/test_alpha31D_pending_clarification_risky_action_coverage.py
- jarvis_v5/tests/smoke/test_alpha31E_parser_signal_consolidation_formworks_guard.py
- jarvis_v5/tests/smoke/test_alpha31F_1_weakness_replay_compatibility.py
- jarvis_v5/tests/smoke/test_alpha35_5_windows_test_report_cleanup.py
- jarvis_v5/tests/smoke/test_alpha28_1_package_hygiene.py
- jarvis_v5/config.py

Protected Builder boundary: unchanged.
Workbook read: false.
Engine called: false.
Excel created: false.
Legacy Builder called: false.

Fix: added test-only safe_rmtree cleanup helper and replaced fragile raw shutil.rmtree calls in affected smoke-test reset helpers.
