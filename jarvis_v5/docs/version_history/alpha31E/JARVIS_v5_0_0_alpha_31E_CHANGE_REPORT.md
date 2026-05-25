# Jarvis v5.0.0-alpha.31E Change Report

## Version

- Version: `v5.0.0-alpha.31E`
- Base: `v5.0.0-alpha.31D`
- Scope: Parser Signal Helper Consolidation + Formworks Unit Conflict Guard, no workbook read.

## Files changed

Runtime/parser/compatibility:

- `jarvis_v5/config.py`
- `jarvis_v5/app.py`
- `jarvis_v5/parsers/setup_signal_helpers.py`
- `jarvis_v5/parsers/trade_parser.py`
- `jarvis_v5/parsers/conflict_guard.py`
- `jarvis_v5/tools/builder/function_unit_compatibility.py`

Tests/packs:

- `jarvis_v5/tests/smoke/test_alpha31E_parser_signal_consolidation_formworks_guard.py`
- `jarvis_v5/tests/packs/alpha31E_parser_function_unit_conflict_tests.json`
- `jarvis_v5/tests/smoke/test_alpha28_1_package_hygiene.py`

Docs/reports/handoff:

- `README.md`
- `jarvis_v5/docs/ALPHA_31E_SCOPE.md`
- `jarvis_v5/docs/PROTECTED_BUILDER_BOUNDARY_HASH_MANIFEST_ALPHA_31E.md`
- `CURRENT_BACKEND_STATUS_v5_alpha_31E.md`
- `NEXT_CHAT_HANDOFF_v5_alpha_31E.md`
- `CHAT_CONTEXT_ARCHIVE_v5_alpha_31E.md`

## Functions added

- `unique_signal_values(...)`
- `detect_trade_signals(...)`
- `detect_function_signals(...)`
- `detect_custom_quantity_signals(...)`
- `detect_unit_signals(...)`
- `has_explicit_reinforcement_weight_t_setup(...)`
- `is_direct_concrete_reo_setup(...)`

## Functions changed

- `parse_trade_function_unit(...)`
- `detect_setup_conflict(...)`
- `allowed_units_for_function(...)`
- `api_version(...)`

## What changed

- Consolidated duplicated parser signal detection into `setup_signal_helpers.py`.
- Preserved existing parser/conflict behavior through helper parameters.
- Added the narrow unit compatibility rule: `XGETCUSTOM + Formworks` allows `m2`.
- `Use XGETCUSTOM Formworks unit t` now blocks with function/unit clarification instead of mutating the Builder plan.
- `Use XGETCUSTOM Formworks unit m2` remains a valid setup edit.

## What was not touched

- Builder formula/export engine.
- CostX formula generation.
- Formula Integrity Guard execution.
- Legacy Builder execution bridge.
- Workbook reader/parser.
- Excel output writer.
- Formatter, QA Checker, O&A, UI, Output Center.
- Safe workbook path resolver behavior.
- Workbook read preflight behavior.
- Preview policy behavior.
- No-active, active non-mutating, feedback, pending clarification, or main router behavior.
