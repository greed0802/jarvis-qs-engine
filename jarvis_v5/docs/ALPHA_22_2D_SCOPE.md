# v5.0.0-alpha.22.2D — High-Priority Ownership Repair + Multi-slot Setup Reducer, no engine

## Base
v5.0.0-alpha.22.2C — Router Language Ownership Cleanup + Active Setup Grammar Normalization, no engine.

## Scope
- Repair feedback ownership so no-active-task writing/help stays under NoActiveTaskLanguageGate.
- Expand missing soft Builder, generic choose_tool, and general QS-help coverage inside NoActiveTaskLanguageGate only.
- Expose existing conflict_guard output through ReducerResult.conflicts and normalization evidence.
- Upgrade setup_text_normalizer to handle multi-clause setup messages without dropping semantic tokens.
- Refactor active setup reducer to collect and apply multiple slot edits from one canonical message in safe order.
- Run conflict checks on both raw and canonical text before mutation.

## Protected / not touched
- No Builder engine.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter.
- No QA Checker.
- No O&A.
- No snapshot/adapter/contract/preflight/execution logic changes.
- No UI redesign.

## Safety locks
workbook_read=false, engine_called=false, excel_created=false, legacy_builder_called=false.
