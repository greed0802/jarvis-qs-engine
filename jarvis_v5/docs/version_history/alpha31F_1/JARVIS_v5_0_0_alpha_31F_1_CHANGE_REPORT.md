# Change Report — v5.0.0-alpha.31F.1

Base: v5.0.0-alpha.31E.

Scope: Weakness Replay Compatibility Cleanup; no route behavior change, no parser behavior change, no workbook read.

## Runtime metadata changed

- `jarvis_v5/config.py` updated to v5.0.0-alpha.31F.1.
- `/api/version` scope metadata updated for weakness replay compatibility cleanup.

## Additive diagnostic alias

- `jarvis_v5/router/main_router.py` now exposes `active_task_action_language.matched=true` for exact active action aliases.
- Routes, messages, blocked status, fallback status, task state, and reducer results are unchanged.

## Documentation

- Added weakness replay version-lock policy and compatibility cleanup documentation.
- Documented alpha.30 reference-pack version-lock artifacts and deferred minimal-pair route ownership.
