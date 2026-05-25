# Targeted Weakness Subset Report — v5.0.0-alpha.31E

## Scope

Targeted parser/function-unit weakness subset only.

## Results

- `041_function_unit_conflict_raw_canonical_1.json`: PASS — 50 / 50
- `042_function_unit_conflict_raw_canonical_2.json`: PASS — 50 / 50
- `043_function_unit_conflict_raw_canonical_3.json`: PASS — 50 / 50
- `044_function_unit_conflict_raw_canonical_4.json`: PASS — 50 / 50
- `045_function_unit_conflict_raw_canonical_5.json`: PASS — 50 / 50

Total: PASS — 250 / 250

## Fixed case

`Use XGETCUSTOM Formworks unit t` now blocks with function/unit clarification.

## Stability check

Selected active route stability subset from alpha.31B/31C/31D also passed: 1000 / 1000.

## Deferred

- Windows BAT validation was not run on Windows.
- Cross-file helper duplicates outside parser signal helpers remain documented only.
