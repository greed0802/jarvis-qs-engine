# Jarvis v5.0.0-alpha.35.7.1 Change Report

Generated: 2026-05-19T10:26:40.523326+00:00

## Version

`v5.0.0-alpha.35.7.1 — Package Hygiene Test Version Lock Cleanup, no behavior change`

## Base used

`v5.0.0-alpha.35.7 — Workbook Read Policy Response Contract Cleanup, no workbook read`

Fallback remains `v5.0.0-alpha.35.5.1`.

## Scope

Test/package hygiene only. This build updates one stale smoke test that still expected alpha.35.6 root release artifacts.

## Files changed

- `jarvis_v5/tests/smoke/test_alpha28_1_package_hygiene.py`

## Function changed

- `test_current_alpha35_6_root_release_artifacts_exist()` renamed/updated to `test_current_alpha35_7_root_release_artifacts_exist()`

## What changed

- The package hygiene test now validates current alpha.35.7 root artifacts.
- The test also confirms `jarvis_v5/docs/version_history/alpha35_6/` exists, proving alpha.35.6 artifacts were archived instead of remaining at package root.

## What was not touched

- No runtime code changed.
- No route ownership changed.
- No workbook access changed.
- No Builder engine, legacy Builder, parser, Formatter, QA, O&A, UI, Output Center, preview policy, safe path resolver, registry execution flags, workbook preflight, workbook policy, or Builder formula/export engine changed.

## Safety boundary

Safety is unchanged and targeted packs kept:

- `workbook_read_any_true=false`
- `engine_called_any_true=false`
- `excel_created_any_true=false`
- `legacy_builder_called_any_true=false`
