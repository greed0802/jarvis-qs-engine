# Jarvis v5.0.0-alpha.35.10.1 Change Report

## Version

`v5.0.0-alpha.35.10.1`

## Base

`v5.0.0-alpha.35.10` built-in pack hygiene package.

## Scope

UAE Podium / Basement floor-level normalization readiness. No workbook read and no Builder engine.

## Runtime changes

- `jarvis_v5/parsers/conflict_guard.py`
  - Narrowed `ambiguous_basement_range` so descending basement ranges such as `B3 to B1` do not require clarification.
  - Ascending basement ranges such as `B2 to B5` still require clarification.
- `jarvis_v5/parsers/level_parser.py`
  - Added narrow `Podium` level token support.

## Tests added

- `jarvis_v5/tests/smoke/test_alpha35_10_1_uae_podium_basement_levels.py`
- `jarvis_v5/tests/packs/alpha35_10_1_uae_podium_basement_level_tests.json`

## Metadata updated

- `APP_VERSION` and test/pack version locks updated to `v5.0.0-alpha.35.10.1`.

## Protected boundaries

- Builder formula/export engine: not touched.
- Workbook access/read/open behavior: not touched.
- Snapshot endpoint logic: not touched.
- Adapter dry-run endpoint logic: not touched.
- Formatter, QA, O&A, UI, Output Center, preview policy, registry execution flags, safe path resolver: not touched.
