# v5.0.0-alpha.9 — Parser Conflict Guard + Setup Normalization, no engine

## Scope

Alpha.9 adds parser safety guards and setup normalization metadata before any real Builder engine connection.

## Added

- Trade/profile conflict guard.
- Function/unit conflict guard.
- Custom quantity/unit conflict guard.
- Heading ambiguity guard.
- Zone/head mismatch guard.
- Ambiguous basement range guard.
- Normalization status in reducer results, `/api/plan`, snapshots, adapter dry run, and review.

## Safety locks

- `workbook_read = false`
- `engine_called = false`
- `excel_created = false`

## Not connected

No Builder engine, Formatter, QA Checker, O&A, workbook reading/parsing, formula generation, Excel output, UI redesign, or current Jarvis replacement.
