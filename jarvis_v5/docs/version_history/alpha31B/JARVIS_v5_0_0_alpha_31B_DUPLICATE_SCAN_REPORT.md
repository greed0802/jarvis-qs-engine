# v5.0.0-alpha.31B Duplicate Scan Report

Duplicate FastAPI routes: 0
Same-file top-level duplicate definitions: 0
Cross-file helper/function duplicate names: 33 documented only

## No-active prompt-injection safe-block refs
- `jarvis_v5/router/main_router.py`
- `jarvis_v5/router/no_active_task_language_gate.py`
- `jarvis_v5/qa_runner/test_executor.py`
- `jarvis_v5/tests/smoke/test_alpha31B_no_active_route_hygiene.py`

## Protected Builder boundary
- `jarvis_v5/tools/builder/adapter_dry_run.py` unchanged=True
- `jarvis_v5/tools/builder/engine_contract_adapter.py` unchanged=True
- `jarvis_v5/tools/builder/engine_preflight.py` unchanged=True
- `jarvis_v5/tools/builder/legacy_engine_bridge.py` unchanged=True
- `jarvis_v5/tools/builder/contract_fixture_replay.py` unchanged=True
- `jarvis_v5/core/snapshot_store.py` unchanged=True
- `jarvis_v5/core/adapter_store.py` unchanged=True
- `jarvis_v5/core/engine_contract_store.py` unchanged=True
- `jarvis_v5/core/engine_preflight_store.py` unchanged=True
- `jarvis_v5/core/engine_execution_store.py` unchanged=True
