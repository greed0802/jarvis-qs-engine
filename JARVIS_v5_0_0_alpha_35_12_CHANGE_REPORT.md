# Jarvis v5.0.0-alpha.35.12 Change Report

## Version

`v5.0.0-alpha.35.12 — Advisory Route Precision + Future Tool Clarification Contract, no execution`

## Base used

`v5.0.0-alpha.35.11 — Metadata-only Capability Advisory + QS Scope/RFI Advisor, no execution`

## Scope

Approved FIRE scope only:

- Metadata-only future-tool clarification contract.
- Unknown QS scope clarification metadata.
- Narrow no-active advisory route precision.
- Alpha35.12 smoke and JSON advisory regression pack.
- Docs/handoff/reports.

## Runtime files changed

- `jarvis_v5/config.py` — version bump only.
- `jarvis_v5/registry/registry_loader.py` — future-tool execution-request metadata and unknown-scope clarification metadata.
- `jarvis_v5/schemas/registry_schema.py` — response schema compatibility for new optional metadata fields.
- `jarvis_v5/router/no_active_task_language_gate.py` — narrow no-active future-tool advisory precision for compare/process old vs revised BOQ prompts.

## Tests added

- `jarvis_v5/tests/smoke/test_alpha35_12_advisory_regression_hardening.py`
- `jarvis_v5/tests/packs/alpha35_12_advisory_regression_hardening_tests.json`

## Retained test maintenance

Retained smoke/JSON pack version assertions were refreshed from alpha35.11 to alpha35.12 so the full pytest suite remains current-version clean.

## Protected systems not touched

```text
Builder formula/export engine
workbook content read/parse
Builder engine
Formatter
QA Checker
O&A
UI
Output Center
preview policy
registry execution flags to true
safe path resolver
workbook policy runtime
Builder reducer/mutation paths
active-task advisory route
main_router.py
```

## Protected hash result

```text
10 / 10 protected Builder boundary files unchanged
all_unchanged=True
```

## Changed files

- added: `CURRENT_BACKEND_STATUS_v5_alpha_35_12.md`
- added: `JARVIS_v5_0_0_alpha_35_12_CHANGED_FILES.json`
- added: `JARVIS_v5_0_0_alpha_35_12_CHANGE_REPORT.md`
- added: `JARVIS_v5_0_0_alpha_35_12_DUPLICATE_SCAN.json`
- added: `JARVIS_v5_0_0_alpha_35_12_DUPLICATE_SCAN_REPORT.md`
- added: `JARVIS_v5_0_0_alpha_35_12_PACKAGE_HYGIENE.json`
- added: `JARVIS_v5_0_0_alpha_35_12_PACKAGE_HYGIENE_REPORT.md`
- added: `JARVIS_v5_0_0_alpha_35_12_PROTECTED_HASH_COMPARE.json`
- added: `JARVIS_v5_0_0_alpha_35_12_TEST_REPORT.md`
- added: `JARVIS_v5_0_0_alpha_35_12_TEST_RUN_RESULTS.txt`
- added: `NEXT_CHAT_HANDOFF_v5_alpha_35_12.md`
- modified: `jarvis_v5/config.py`
- added: `jarvis_v5/docs/ALPHA_35_12_SCOPE.md`
- modified: `jarvis_v5/registry/registry_loader.py`
- modified: `jarvis_v5/router/no_active_task_language_gate.py`
- modified: `jarvis_v5/schemas/registry_schema.py`
- modified: `jarvis_v5/tests/fixtures/contracts/wall_types_xgetwallarea_zone1_head2_gf_l3_contract_v1.json`
- modified: `jarvis_v5/tests/packs/alpha11_contract_negative_guards.json`
- modified: `jarvis_v5/tests/packs/alpha15_review_readiness_tests.json`
- modified: `jarvis_v5/tests/packs/alpha16_engine_preflight_tests.json`
- modified: `jarvis_v5/tests/packs/alpha17_engine_execution_lock_tests.json`
- modified: `jarvis_v5/tests/packs/alpha18_1_safety_envelope_tests.json`
- modified: `jarvis_v5/tests/packs/alpha18_response_consistency_tests.json`
- modified: `jarvis_v5/tests/packs/alpha19_contract_fixture_replay_tests.json`
- modified: `jarvis_v5/tests/packs/alpha20_deep_weak_point_boundary_tests.json`
- modified: `jarvis_v5/tests/packs/alpha20_legacy_import_boundary_audit_tests.json`
- modified: `jarvis_v5/tests/packs/alpha21_function_unit_compatibility_tests.json`
- modified: `jarvis_v5/tests/packs/alpha22_1_no_fallback_router_tightening_tests.json`
- modified: `jarvis_v5/tests/packs/alpha22_2a_router_confidence_shadow_tests.json`
- modified: `jarvis_v5/tests/packs/alpha22_2b_limited_control_router_tests.json`
- modified: `jarvis_v5/tests/packs/alpha22_2c_route_ownership_and_setup_normalization_tests.json`
- modified: `jarvis_v5/tests/packs/alpha22_2d_high_priority_ownership_repair_tests.json`
- modified: `jarvis_v5/tests/packs/alpha22_2e_active_task_language_plan_cleanup_tests.json`
- modified: `jarvis_v5/tests/packs/alpha22_2f_engineering_language_gate_tests.json`
- modified: `jarvis_v5/tests/packs/alpha22_qs_intent_alias_router_tests.json`
- modified: `jarvis_v5/tests/packs/alpha23_global_capability_registry_tests.json`
- modified: `jarvis_v5/tests/packs/alpha24_route_ownership_registry_advisory_tests.json`
- modified: `jarvis_v5/tests/packs/alpha25_legacy_bridge_readiness_audit_tests.json`
- modified: `jarvis_v5/tests/packs/alpha26_1_response_schema_pack_hygiene_tests.json`
- modified: `jarvis_v5/tests/packs/alpha26_legacy_bridge_shadow_probe_tests.json`
- modified: `jarvis_v5/tests/packs/alpha27_preview_execution_policy_tests.json`
- modified: `jarvis_v5/tests/packs/alpha28_1_package_hygiene_tests.json`
- modified: `jarvis_v5/tests/packs/alpha28_policy_response_hygiene_approval_readiness_tests.json`
- modified: `jarvis_v5/tests/packs/alpha29_safe_workbook_path_resolver_dry_run_tests.json`
- modified: `jarvis_v5/tests/packs/alpha30_1_weakness_triage_reduced_regression_tests.json`
- modified: `jarvis_v5/tests/packs/alpha30_workbook_read_preflight_contract_tests.json`
- modified: `jarvis_v5/tests/packs/alpha31A_response_shape_compatibility_tests.json`
- modified: `jarvis_v5/tests/packs/alpha31B_no_active_route_hygiene_tests.json`
- modified: `jarvis_v5/tests/packs/alpha31C_active_non_mutating_feedback_read_only_tests.json`
- modified: `jarvis_v5/tests/packs/alpha31D_pending_clarification_risky_action_coverage_tests.json`
- modified: `jarvis_v5/tests/packs/alpha31E_parser_function_unit_conflict_tests.json`
- modified: `jarvis_v5/tests/packs/alpha31F_1_weakness_replay_compatibility_tests.json`
- modified: `jarvis_v5/tests/packs/alpha32A_minimal_pair_route_ownership_tests.json`
- modified: `jarvis_v5/tests/packs/alpha33_workbook_metadata_probe_approval_tests.json`
- modified: `jarvis_v5/tests/packs/alpha34_workbook_sheet_name_probe_approval_tests.json`
- modified: `jarvis_v5/tests/packs/alpha35_10_1_uae_podium_basement_level_tests.json`
- modified: `jarvis_v5/tests/packs/alpha35_10_2_active_writing_report_preview_false_positive_tests.json`
- modified: `jarvis_v5/tests/packs/alpha35_10_no_active_mixed_language_policy_route_tests.json`
- modified: `jarvis_v5/tests/packs/alpha35_11_capability_advisory_tests.json`
- added: `jarvis_v5/tests/packs/alpha35_12_advisory_regression_hardening_tests.json`
- modified: `jarvis_v5/tests/packs/alpha35_8_workbook_read_policy_plan_visibility_tests.json`
- modified: `jarvis_v5/tests/packs/alpha35_9_pending_clarification_policy_action_ownership_tests.json`
- modified: `jarvis_v5/tests/packs/alpha35_workbook_read_policy_review_tests.json`
- modified: `jarvis_v5/tests/packs/sample_external_ai_pack_valid.json`
- modified: `jarvis_v5/tests/smoke/test_alpha16_engine_preflight.py`
- modified: `jarvis_v5/tests/smoke/test_alpha17_engine_execution_lock.py`
- modified: `jarvis_v5/tests/smoke/test_alpha18_1_safety_envelope.py`
- modified: `jarvis_v5/tests/smoke/test_alpha18_response_consistency.py`
- modified: `jarvis_v5/tests/smoke/test_alpha19_contract_fixture_replay.py`
- modified: `jarvis_v5/tests/smoke/test_alpha20_legacy_import_boundary_audit.py`
- modified: `jarvis_v5/tests/smoke/test_alpha21_function_unit_compatibility.py`
- modified: `jarvis_v5/tests/smoke/test_alpha22_1_no_fallback_router_tightening.py`
- modified: `jarvis_v5/tests/smoke/test_alpha22_2a_router_confidence_shadow.py`
- modified: `jarvis_v5/tests/smoke/test_alpha22_2b_limited_control_router.py`
- modified: `jarvis_v5/tests/smoke/test_alpha22_2c_route_ownership_and_setup_normalization.py`
- modified: `jarvis_v5/tests/smoke/test_alpha22_2d_high_priority_ownership_repair.py`
- modified: `jarvis_v5/tests/smoke/test_alpha22_2e_active_task_language_plan_cleanup.py`
- modified: `jarvis_v5/tests/smoke/test_alpha22_2f_engineering_language_gate.py`
- modified: `jarvis_v5/tests/smoke/test_alpha22_qs_intent_alias_router.py`
- modified: `jarvis_v5/tests/smoke/test_alpha23_global_capability_registry.py`
- modified: `jarvis_v5/tests/smoke/test_alpha24_2_cleanup_hygiene.py`
- modified: `jarvis_v5/tests/smoke/test_alpha24_route_ownership_registry_advisory.py`
- modified: `jarvis_v5/tests/smoke/test_alpha25_legacy_bridge_readiness_audit.py`
- modified: `jarvis_v5/tests/smoke/test_alpha26_1_response_schema_pack_hygiene.py`
- modified: `jarvis_v5/tests/smoke/test_alpha26_legacy_bridge_shadow_probe.py`
- modified: `jarvis_v5/tests/smoke/test_alpha27_preview_execution_policy.py`
- modified: `jarvis_v5/tests/smoke/test_alpha28_1_package_hygiene.py`
- modified: `jarvis_v5/tests/smoke/test_alpha28_policy_response_hygiene_approval_readiness.py`
- modified: `jarvis_v5/tests/smoke/test_alpha29_safe_workbook_path_resolver_dry_run.py`
- modified: `jarvis_v5/tests/smoke/test_alpha30_workbook_read_preflight_contract.py`
- modified: `jarvis_v5/tests/smoke/test_alpha31A_response_shape_compatibility.py`
- modified: `jarvis_v5/tests/smoke/test_alpha31B_no_active_route_hygiene.py`
- modified: `jarvis_v5/tests/smoke/test_alpha31C_active_non_mutating_feedback_read_only.py`
- modified: `jarvis_v5/tests/smoke/test_alpha31D_pending_clarification_risky_action_coverage.py`
- modified: `jarvis_v5/tests/smoke/test_alpha31E_parser_signal_consolidation_formworks_guard.py`
- modified: `jarvis_v5/tests/smoke/test_alpha31F_1_weakness_replay_compatibility.py`
- modified: `jarvis_v5/tests/smoke/test_alpha32A_minimal_pair_route_ownership.py`
- modified: `jarvis_v5/tests/smoke/test_alpha33_workbook_metadata_probe_approval.py`
- modified: `jarvis_v5/tests/smoke/test_alpha34_workbook_sheet_name_probe_approval.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_10_1_uae_podium_basement_levels.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_10_2_active_writing_report_preview_false_positive.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_10_no_active_mixed_language_policy_route.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_11_capability_advisory.py`
- added: `jarvis_v5/tests/smoke/test_alpha35_12_advisory_regression_hardening.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_2_conversation_id_sanitization.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_3_no_active_workbook_read_policy_routing.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_4_no_active_sheet_name_probe_ambiguity.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_5_active_workbook_read_policy_non_mutating.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_6_active_content_read_safe_block.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_8_workbook_read_policy_plan_visibility.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_9_pending_clarification_policy_action_ownership.py`
- modified: `jarvis_v5/tests/smoke/test_alpha35_workbook_read_policy_review.py`
