# Jarvis v5.0.0-alpha.30.1 Duplicate Scan Report

- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file helper/function duplicate names: 33 documented only

## Cross-file duplicate policy

Cross-file helper duplicates are documented only. No helper renames were made in alpha.30.1.

- `_blocked_by_policy`: jarvis_v5/tools/builder/legacy_bridge_shadow_probe.py:91, jarvis_v5/tools/builder/preview_execution_policy.py:224
- `_chat`: jarvis_v5/tests/smoke/test_alpha27_preview_execution_policy.py:11, jarvis_v5/tests/smoke/test_alpha28_policy_response_hygiene_approval_readiness.py:25
- `_client`: jarvis_v5/tests/smoke/test_alpha27_preview_execution_policy.py:7, jarvis_v5/tests/smoke/test_alpha28_policy_response_hygiene_approval_readiness.py:21
- `_contract_payload`: jarvis_v5/tools/builder/legacy_bridge_shadow_probe.py:44, jarvis_v5/tools/builder/preview_execution_policy.py:37
- `_detect_custom_quantities`: jarvis_v5/parsers/trade_parser.py:57, jarvis_v5/parsers/conflict_guard.py:88
- `_detect_functions`: jarvis_v5/parsers/trade_parser.py:49, jarvis_v5/parsers/conflict_guard.py:80
- `_detect_trades`: jarvis_v5/parsers/trade_parser.py:41, jarvis_v5/parsers/conflict_guard.py:46
- `_detect_units`: jarvis_v5/parsers/trade_parser.py:61, jarvis_v5/parsers/conflict_guard.py:92
- `_has_explicit_reinforcement_weight_t_setup`: jarvis_v5/parsers/trade_parser.py:79, jarvis_v5/parsers/conflict_guard.py:131
- `_is_direct_concrete_reo_setup`: jarvis_v5/parsers/trade_parser.py:84, jarvis_v5/parsers/conflict_guard.py:136
- `_norm`: jarvis_v5/registry/trade_profile_registry.py:24, jarvis_v5/registry/registry_loader.py:120
- `_now`: jarvis_v5/reducers/slot_reducer.py:24, jarvis_v5/parsers/conflict_guard.py:34, jarvis_v5/registry/trade_profile_registry.py:14, jarvis_v5/tools/builder/function_unit_compatibility.py:55
- `_public_workbook_ref`: jarvis_v5/tools/builder/contract_fixture_replay.py:81, jarvis_v5/tools/builder/preview_execution_policy.py:83
- `_unique`: jarvis_v5/parsers/trade_parser.py:33, jarvis_v5/parsers/conflict_guard.py:38
- `_word_pattern`: jarvis_v5/parsers/conflict_guard.py:50, jarvis_v5/registry/trade_profile_registry.py:28
- `adapter_dry_run`: jarvis_v5/tests/smoke/test_alpha5_builder_adapter_dry_run.py:24, jarvis_v5/tests/smoke/test_alpha51_adapter_freshness.py:24, jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:35, jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:36, jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:31, jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:38
- `assert_safety`: jarvis_v5/tests/smoke/test_alpha18_1_safety_envelope.py:25, jarvis_v5/tests/smoke/test_alpha19_contract_fixture_replay.py:45, jarvis_v5/tests/smoke/test_alpha20_legacy_import_boundary_audit.py:29, jarvis_v5/tests/smoke/test_alpha21_function_unit_compatibility.py:55
- `assert_safety_false`: jarvis_v5/tests/smoke/test_alpha17_engine_execution_lock.py:52, jarvis_v5/tests/smoke/test_alpha18_response_consistency.py:30
- `attach_fixture`: jarvis_v5/tests/smoke/test_alpha15_review_readiness.py:19, jarvis_v5/tests/smoke/test_alpha16_engine_preflight.py:20, jarvis_v5/tests/smoke/test_alpha17_engine_execution_lock.py:19, jarvis_v5/tests/smoke/test_alpha18_response_consistency.py:19, jarvis_v5/tests/smoke/test_alpha22_2d_high_priority_ownership_repair.py:18
- `attach_workbook`: jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:20, jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:21, jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:19, jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:22, jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:22, jarvis_v5/tests/smoke/test_alpha13_engine_boundary_audit.py:22
- `canonical_hash`: jarvis_v5/schemas/builder_snapshot_schema.py:16, jarvis_v5/schemas/builder_engine_contract_schema.py:15
- `client`: jarvis_v5/tests/smoke/test_alpha1_state_router.py:17, jarvis_v5/tests/smoke/test_alpha2_active_router.py:17, jarvis_v5/tests/smoke/test_alpha3_slot_reducer.py:15, jarvis_v5/tests/smoke/test_alpha4_builder_snapshot.py:22, jarvis_v5/tests/smoke/test_alpha41_snapshot_stale.py:6, jarvis_v5/tests/smoke/test_alpha5_builder_adapter_dry_run.py:6
- `complete_setup`: jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:52, jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:52
- `complete_wall_types_setup`: jarvis_v5/tests/smoke/test_alpha15_review_readiness.py:26, jarvis_v5/tests/smoke/test_alpha16_engine_preflight.py:31
- `create_snapshot`: jarvis_v5/tests/smoke/test_alpha41_snapshot_stale.py:17, jarvis_v5/tests/smoke/test_alpha5_builder_adapter_dry_run.py:17, jarvis_v5/tests/smoke/test_alpha51_adapter_freshness.py:17, jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:28, jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:29, jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:27
- `create_task`: jarvis_v5/tests/smoke/test_alpha2_active_router.py:23, jarvis_v5/tests/smoke/test_alpha3_slot_reducer.py:25, jarvis_v5/tests/smoke/test_alpha9_parser_conflict_guard.py:17
- `engine_contract`: jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:45, jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:45
- `now_iso`: jarvis_v5/core/attachment_store.py:12, jarvis_v5/core/event_ledger.py:11, jarvis_v5/core/adapter_store.py:11, jarvis_v5/core/engine_contract_store.py:11, jarvis_v5/core/engine_preflight_store.py:11, jarvis_v5/core/engine_execution_store.py:11
- `post`: jarvis_v5/tests/smoke/test_alpha3_slot_reducer.py:21, jarvis_v5/tests/smoke/test_alpha4_builder_snapshot.py:28, jarvis_v5/tests/smoke/test_alpha41_snapshot_stale.py:10, jarvis_v5/tests/smoke/test_alpha9_parser_conflict_guard.py:9, jarvis_v5/tests/smoke/test_alpha21_function_unit_compatibility.py:13, jarvis_v5/tests/smoke/test_alpha22_qs_intent_alias_router.py:11
- `post_chat`: jarvis_v5/tests/smoke/test_alpha5_builder_adapter_dry_run.py:10, jarvis_v5/tests/smoke/test_alpha51_adapter_freshness.py:10, jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:13, jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:14, jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:15, jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:14
- `reset_data`: jarvis_v5/tests/smoke/test_alpha1_state_router.py:10, jarvis_v5/tests/smoke/test_alpha2_active_router.py:10, jarvis_v5/tests/smoke/test_alpha3_slot_reducer.py:8, jarvis_v5/tests/smoke/test_alpha4_builder_snapshot.py:8
- `start_builder`: jarvis_v5/tests/smoke/test_alpha22_2d_high_priority_ownership_repair.py:27, jarvis_v5/tests/smoke/test_alpha22_2e_active_task_language_plan_cleanup.py:15, jarvis_v5/tests/smoke/test_alpha22_2f_engineering_language_gate.py:15
- `start_complete_wall_types`: jarvis_v5/tests/smoke/test_alpha18_1_safety_envelope.py:10, jarvis_v5/tests/smoke/test_alpha19_contract_fixture_replay.py:10, jarvis_v5/tests/smoke/test_alpha20_legacy_import_boundary_audit.py:10
