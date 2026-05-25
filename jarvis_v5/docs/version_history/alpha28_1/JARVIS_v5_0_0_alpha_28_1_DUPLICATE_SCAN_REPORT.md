# Duplicate Scan Report — v5.0.0-alpha.28.1

Scope: Package Artifact Deduplication + Helper Duplicate Audit, no behavior change.

## Summary

| Scan | Result |
|---|---:|
| Duplicate FastAPI routes | 0 |
| Same-file duplicate top-level definitions | 0 |
| Cross-file duplicate top-level helper/function names | 33 |
| Preview-policy owner conflict | 0 |
| Previous-version root artifacts after cleanup | 0 |

## FastAPI route duplicate scan

Result: **PASS** — no duplicate FastAPI routes found.

```text
{}
```

## Same-file top-level duplicate definition scan

Result: **PASS** — no same-file top-level duplicate function/class definitions found.

```text
[]
```

## Preview-policy route owner scan

Result: **PASS** — `/api/builder/preview-execution-policy` is exposed by `jarvis_v5/app.py` and policy logic remains owned by `jarvis_v5/tools/builder/preview_execution_policy.py`.

References found:

```text
jarvis_v5/app.py
jarvis_v5/qa_runner/test_executor.py
jarvis_v5/tests/smoke/test_alpha27_preview_execution_policy.py
jarvis_v5/tests/smoke/test_alpha28_policy_response_hygiene_approval_readiness.py
jarvis_v5/tests/smoke/test_alpha28_1_package_hygiene.py
jarvis_v5/tools/builder/preview_execution_policy.py
```

## Previous-version root artifact scan

Result: **PASS** — no alpha.27 or alpha.28 root release artifacts remain in the final alpha.28.1 root.

Stale root artifacts after cleanup:

```text
[]
```

## Cross-file helper/function duplicates

These are documented only. Alpha.28.1 intentionally does not rename helpers or change runtime behavior.

| Name | File count | Risk | Family | Locations |
|---|---:|---|---|---|
| `_blocked_by_policy` | 2 | Medium-low | runtime/shared helper | jarvis_v5/tools/builder/legacy_bridge_shadow_probe.py:91; jarvis_v5/tools/builder/preview_execution_policy.py:224 |
| `_chat` | 2 | Low | test helper | jarvis_v5/tests/smoke/test_alpha27_preview_execution_policy.py:11; jarvis_v5/tests/smoke/test_alpha28_policy_response_hygiene_approval_readiness.py:25 |
| `_client` | 2 | Low | test helper | jarvis_v5/tests/smoke/test_alpha27_preview_execution_policy.py:7; jarvis_v5/tests/smoke/test_alpha28_policy_response_hygiene_approval_readiness.py:21 |
| `_contract_payload` | 2 | Medium-low | runtime/shared helper | jarvis_v5/tools/builder/legacy_bridge_shadow_probe.py:44; jarvis_v5/tools/builder/preview_execution_policy.py:37 |
| `_detect_custom_quantities` | 2 | Medium | parser/conflict helper | jarvis_v5/parsers/trade_parser.py:57; jarvis_v5/parsers/conflict_guard.py:88 |
| `_detect_functions` | 2 | Medium | parser/conflict helper | jarvis_v5/parsers/trade_parser.py:49; jarvis_v5/parsers/conflict_guard.py:80 |
| `_detect_trades` | 2 | Medium | parser/conflict helper | jarvis_v5/parsers/trade_parser.py:41; jarvis_v5/parsers/conflict_guard.py:46 |
| `_detect_units` | 2 | Medium | parser/conflict helper | jarvis_v5/parsers/trade_parser.py:61; jarvis_v5/parsers/conflict_guard.py:92 |
| `_has_explicit_reinforcement_weight_t_setup` | 2 | Medium | parser/conflict helper | jarvis_v5/parsers/trade_parser.py:79; jarvis_v5/parsers/conflict_guard.py:131 |
| `_is_direct_concrete_reo_setup` | 2 | Medium | parser/conflict helper | jarvis_v5/parsers/trade_parser.py:84; jarvis_v5/parsers/conflict_guard.py:136 |
| `_norm` | 2 | Medium-low | runtime/shared helper | jarvis_v5/registry/trade_profile_registry.py:24; jarvis_v5/registry/registry_loader.py:120 |
| `_now` | 4 | Medium | parser/conflict helper | jarvis_v5/reducers/slot_reducer.py:24; jarvis_v5/parsers/conflict_guard.py:34; jarvis_v5/registry/trade_profile_registry.py:14; jarvis_v5/tools/builder/function_unit_compatibility.py:55 |
| `_public_workbook_ref` | 2 | Medium-low | runtime/shared helper | jarvis_v5/tools/builder/contract_fixture_replay.py:81; jarvis_v5/tools/builder/preview_execution_policy.py:83 |
| `_unique` | 2 | Medium | parser/conflict helper | jarvis_v5/parsers/trade_parser.py:33; jarvis_v5/parsers/conflict_guard.py:38 |
| `_word_pattern` | 2 | Medium | parser/conflict helper | jarvis_v5/parsers/conflict_guard.py:50; jarvis_v5/registry/trade_profile_registry.py:28 |
| `adapter_dry_run` | 7 | Low | test helper | jarvis_v5/tests/smoke/test_alpha5_builder_adapter_dry_run.py:24; jarvis_v5/tests/smoke/test_alpha51_adapter_freshness.py:24; jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:35; jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:36; jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:31; jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:38; jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:38 |
| `assert_safety` | 4 | Low | test helper | jarvis_v5/tests/smoke/test_alpha18_1_safety_envelope.py:25; jarvis_v5/tests/smoke/test_alpha19_contract_fixture_replay.py:45; jarvis_v5/tests/smoke/test_alpha20_legacy_import_boundary_audit.py:29; jarvis_v5/tests/smoke/test_alpha21_function_unit_compatibility.py:55 |
| `assert_safety_false` | 2 | Low | test helper | jarvis_v5/tests/smoke/test_alpha17_engine_execution_lock.py:52; jarvis_v5/tests/smoke/test_alpha18_response_consistency.py:30 |
| `attach_fixture` | 5 | Low | test helper | jarvis_v5/tests/smoke/test_alpha15_review_readiness.py:19; jarvis_v5/tests/smoke/test_alpha16_engine_preflight.py:20; jarvis_v5/tests/smoke/test_alpha17_engine_execution_lock.py:19; jarvis_v5/tests/smoke/test_alpha18_response_consistency.py:19; jarvis_v5/tests/smoke/test_alpha22_2d_high_priority_ownership_repair.py:18 |
| `attach_workbook` | 7 | Low | test helper | jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:20; jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:21; jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:19; jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:22; jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:22; jarvis_v5/tests/smoke/test_alpha13_engine_boundary_audit.py:22; jarvis_v5/tests/smoke/test_alpha14_trade_profile_registry.py:23 |
| `canonical_hash` | 2 | Medium-low | runtime/shared helper | jarvis_v5/schemas/builder_snapshot_schema.py:16; jarvis_v5/schemas/builder_engine_contract_schema.py:15 |
| `client` | 34 | Low | test helper | jarvis_v5/tests/smoke/test_alpha1_state_router.py:17; jarvis_v5/tests/smoke/test_alpha2_active_router.py:17; jarvis_v5/tests/smoke/test_alpha3_slot_reducer.py:15; jarvis_v5/tests/smoke/test_alpha4_builder_snapshot.py:22; jarvis_v5/tests/smoke/test_alpha41_snapshot_stale.py:6; jarvis_v5/tests/smoke/test_alpha5_builder_adapter_dry_run.py:6; jarvis_v5/tests/smoke/test_alpha51_adapter_freshness.py:6; jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:9; jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:10; jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:11; jarvis_v5/tests/smoke/test_alpha9_parser_conflict_guard.py:5; jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:10; jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:10; jarvis_v5/tests/smoke/test_alpha13_engine_boundary_audit.py:10; jarvis_v5/tests/smoke/test_alpha14_trade_profile_registry.py:11; jarvis_v5/tests/smoke/test_alpha15_review_readiness.py:9; jarvis_v5/tests/smoke/test_alpha16_engine_preflight.py:10; jarvis_v5/tests/smoke/test_alpha17_engine_execution_lock.py:9; jarvis_v5/tests/smoke/test_alpha18_response_consistency.py:9; jarvis_v5/tests/smoke/test_alpha18_1_safety_envelope.py:6; jarvis_v5/tests/smoke/test_alpha19_contract_fixture_replay.py:6; jarvis_v5/tests/smoke/test_alpha20_legacy_import_boundary_audit.py:6; jarvis_v5/tests/smoke/test_alpha21_function_unit_compatibility.py:9; jarvis_v5/tests/smoke/test_alpha22_qs_intent_alias_router.py:7; jarvis_v5/tests/smoke/test_alpha22_1_no_fallback_router_tightening.py:7; jarvis_v5/tests/smoke/test_alpha22_2a_router_confidence_shadow.py:7; jarvis_v5/tests/smoke/test_alpha22_2b_limited_control_router.py:7; jarvis_v5/tests/smoke/test_alpha22_2c_route_ownership_and_setup_normalization.py:7; jarvis_v5/tests/smoke/test_alpha22_2d_high_priority_ownership_repair.py:7; jarvis_v5/tests/smoke/test_alpha22_2e_active_task_language_plan_cleanup.py:7; jarvis_v5/tests/smoke/test_alpha22_2f_engineering_language_gate.py:7; jarvis_v5/tests/smoke/test_alpha23_global_capability_registry.py:7; jarvis_v5/tests/smoke/test_alpha24_route_ownership_registry_advisory.py:7; jarvis_v5/tests/smoke/test_alpha26_1_response_schema_pack_hygiene.py:8 |
| `complete_setup` | 2 | Low | test helper | jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:52; jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:52 |
| `complete_wall_types_setup` | 2 | Low | test helper | jarvis_v5/tests/smoke/test_alpha15_review_readiness.py:26; jarvis_v5/tests/smoke/test_alpha16_engine_preflight.py:31 |
| `create_snapshot` | 8 | Low | test helper | jarvis_v5/tests/smoke/test_alpha41_snapshot_stale.py:17; jarvis_v5/tests/smoke/test_alpha5_builder_adapter_dry_run.py:17; jarvis_v5/tests/smoke/test_alpha51_adapter_freshness.py:17; jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:28; jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:29; jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:27; jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:30; jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:30 |
| `create_task` | 3 | Low | test helper | jarvis_v5/tests/smoke/test_alpha2_active_router.py:23; jarvis_v5/tests/smoke/test_alpha3_slot_reducer.py:25; jarvis_v5/tests/smoke/test_alpha9_parser_conflict_guard.py:17 |
| `engine_contract` | 2 | Low | test helper | jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:45; jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:45 |
| `now_iso` | 16 | Medium-low | runtime/shared helper | jarvis_v5/core/attachment_store.py:12; jarvis_v5/core/event_ledger.py:11; jarvis_v5/core/adapter_store.py:11; jarvis_v5/core/engine_contract_store.py:11; jarvis_v5/core/engine_preflight_store.py:11; jarvis_v5/core/engine_execution_store.py:11; jarvis_v5/schemas/conversation_schema.py:8; jarvis_v5/schemas/active_task_schema.py:24; jarvis_v5/schemas/builder_snapshot_schema.py:12; jarvis_v5/schemas/builder_adapter_schema.py:9; jarvis_v5/schemas/builder_engine_contract_schema.py:11; jarvis_v5/tools/builder/engine_preflight.py:24; jarvis_v5/tools/builder/legacy_engine_bridge.py:25; jarvis_v5/tools/builder/legacy_import_boundary_audit.py:60; jarvis_v5/tools/builder/legacy_bridge_shadow_probe.py:36; jarvis_v5/tools/builder/preview_execution_policy.py:29 |
| `post` | 13 | Low | test helper | jarvis_v5/tests/smoke/test_alpha3_slot_reducer.py:21; jarvis_v5/tests/smoke/test_alpha4_builder_snapshot.py:28; jarvis_v5/tests/smoke/test_alpha41_snapshot_stale.py:10; jarvis_v5/tests/smoke/test_alpha9_parser_conflict_guard.py:9; jarvis_v5/tests/smoke/test_alpha21_function_unit_compatibility.py:13; jarvis_v5/tests/smoke/test_alpha22_qs_intent_alias_router.py:11; jarvis_v5/tests/smoke/test_alpha22_1_no_fallback_router_tightening.py:11; jarvis_v5/tests/smoke/test_alpha22_2a_router_confidence_shadow.py:11; jarvis_v5/tests/smoke/test_alpha22_2b_limited_control_router.py:11; jarvis_v5/tests/smoke/test_alpha22_2c_route_ownership_and_setup_normalization.py:11; jarvis_v5/tests/smoke/test_alpha22_2d_high_priority_ownership_repair.py:11; jarvis_v5/tests/smoke/test_alpha22_2e_active_task_language_plan_cleanup.py:11; jarvis_v5/tests/smoke/test_alpha22_2f_engineering_language_gate.py:11 |
| `post_chat` | 13 | Low | test helper | jarvis_v5/tests/smoke/test_alpha5_builder_adapter_dry_run.py:10; jarvis_v5/tests/smoke/test_alpha51_adapter_freshness.py:10; jarvis_v5/tests/smoke/test_alpha6_attachment_binding.py:13; jarvis_v5/tests/smoke/test_alpha7_setup_completeness.py:14; jarvis_v5/tests/smoke/test_alpha8_slot_parser_expansion.py:15; jarvis_v5/tests/smoke/test_alpha10_engine_contract_adapter.py:14; jarvis_v5/tests/smoke/test_alpha11_contract_negative_guards.py:14; jarvis_v5/tests/smoke/test_alpha13_engine_boundary_audit.py:14; jarvis_v5/tests/smoke/test_alpha14_trade_profile_registry.py:15; jarvis_v5/tests/smoke/test_alpha15_review_readiness.py:13; jarvis_v5/tests/smoke/test_alpha16_engine_preflight.py:14; jarvis_v5/tests/smoke/test_alpha17_engine_execution_lock.py:13; jarvis_v5/tests/smoke/test_alpha18_response_consistency.py:13 |
| `reset_data` | 4 | Low | test helper | jarvis_v5/tests/smoke/test_alpha1_state_router.py:10; jarvis_v5/tests/smoke/test_alpha2_active_router.py:10; jarvis_v5/tests/smoke/test_alpha3_slot_reducer.py:8; jarvis_v5/tests/smoke/test_alpha4_builder_snapshot.py:8 |
| `start_builder` | 3 | Low | test helper | jarvis_v5/tests/smoke/test_alpha22_2d_high_priority_ownership_repair.py:27; jarvis_v5/tests/smoke/test_alpha22_2e_active_task_language_plan_cleanup.py:15; jarvis_v5/tests/smoke/test_alpha22_2f_engineering_language_gate.py:15 |
| `start_complete_wall_types` | 3 | Low | test helper | jarvis_v5/tests/smoke/test_alpha18_1_safety_envelope.py:10; jarvis_v5/tests/smoke/test_alpha19_contract_fixture_replay.py:10; jarvis_v5/tests/smoke/test_alpha20_legacy_import_boundary_audit.py:10 |

## Deferred recommendations

- Keep test-helper duplicates as low-risk unless test maintenance becomes difficult.
- Do not consolidate parser/conflict helpers without a dedicated Builder parser dry run and regression pack.
- Do not rename runtime/shared helpers inside a package-hygiene build.
