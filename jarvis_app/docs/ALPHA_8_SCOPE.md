# v5.0.0-alpha.8 — Builder Setup Slot Parser Expansion, no engine

## Goal

Expand the v5 Builder shell parser/reducer so setup slots are captured before any real Builder engine connection.

## Added

- Trade/profile parser updates.
- CostX function/custom quantity/unit parser updates.
- Heading assignment parser.
- Level parser expansion.
- Basic alias parser.
- Shell-plan propagation to `/api/plan`, Review, BuilderRunSnapshot, adapter dry run, and setup completeness.

## Safety

- No Builder engine.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- Preview/Export remain safe stubs.
- `workbook_read=false`, `engine_called=false`, `excel_created=false`.
