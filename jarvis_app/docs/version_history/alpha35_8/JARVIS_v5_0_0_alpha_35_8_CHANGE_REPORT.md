# Jarvis v5.0.0-alpha.35.8 Change Report

Base: v5.0.0-alpha.35.7.1

Scope: Workbook Read Policy Plan Visibility, no execution, no workbook read.

Changed runtime files:
- jarvis_v5/config.py
- jarvis_v5/app.py
- jarvis_v5/core/readiness_contract.py
- jarvis_v5/router/main_router.py

Changed/added tests:
- jarvis_v5/tests/smoke/test_alpha35_8_workbook_read_policy_plan_visibility.py
- jarvis_v5/tests/packs/alpha35_8_workbook_read_policy_plan_visibility_tests.json
- version target updates in tests/packs
- package hygiene test current artifact expectation updated to alpha.35.8

Protected behavior:
- No workbook read enabled
- No Builder engine call
- No Excel output
- No legacy Builder call
- No route ownership change
- No sheet-name probe behavior change
- No pending clarification behavior change
