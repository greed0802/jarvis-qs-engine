# Current Backend Status — v5.0.0-alpha.31E

Current version: `v5.0.0-alpha.31E`

Scope: Parser Signal Helper Consolidation + Formworks Unit Conflict Guard, no workbook read.

## Current safety locks

- `WORKBOOK_READ_ENABLED = False`
- `BUILDER_ENGINE_EXECUTION_ENABLED = False`
- `LEGACY_BUILDER_CALLABLE = False`
- `EXCEL_OUTPUT_ENABLED = False`

## Current status

- Parser signal helper owner added: `jarvis_v5/parsers/setup_signal_helpers.py`
- Trade parser and conflict guard now share parser signal helper ownership.
- `XGETCUSTOM + Formworks` now allows only `m2`.
- `Use XGETCUSTOM Formworks unit t` now clarifies instead of mutating.
- Workbook read, Builder engine, legacy Builder, and Excel output remain disabled.

## Deferred

- Windows BAT scripts were created but not run on Windows.
- Remaining cross-file helper duplicates are documented only.
