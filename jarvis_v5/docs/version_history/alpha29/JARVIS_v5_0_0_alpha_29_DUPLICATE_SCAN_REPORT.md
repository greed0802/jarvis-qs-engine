# Duplicate / Owner Scan Report — v5.0.0-alpha.29

Generated: 2026-05-17T13:09:03.735028Z

- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file duplicate helper/function names: 33 documented only
- Safe workbook path resolver endpoint refs: ['jarvis_v5/app.py', 'jarvis_v5/qa_runner/test_executor.py', 'jarvis_v5/tests/smoke/test_alpha29_safe_workbook_path_resolver_dry_run.py']
- Safe workbook path resolver logic refs: ['jarvis_v5/app.py', 'jarvis_v5/tests/smoke/test_alpha29_safe_workbook_path_resolver_dry_run.py', 'jarvis_v5/tools/builder/safe_workbook_path_resolver.py']
- Protected Builder boundary hash check: 10 / 10

## Cross-file helper duplicates

These remain documented-only and were not changed in alpha.29.

```text
_blocked_by_policy
_chat
_client
_contract_payload
_detect_custom_quantities
_detect_functions
_detect_trades
_detect_units
_has_explicit_reinforcement_weight_t_setup
_is_direct_concrete_reo_setup
_norm
_now
_public_workbook_ref
_unique
_word_pattern
adapter_dry_run
assert_safety
assert_safety_false
attach_fixture
attach_workbook
canonical_hash
client
complete_setup
complete_wall_types_setup
create_snapshot
create_task
engine_contract
now_iso
post
post_chat
reset_data
start_builder
start_complete_wall_types
```

## Route owner result

`app.py` exposes `/api/builder/safe-workbook-path-resolver-dry-run`.

`jarvis_v5/tools/builder/safe_workbook_path_resolver.py` owns resolver behavior.
