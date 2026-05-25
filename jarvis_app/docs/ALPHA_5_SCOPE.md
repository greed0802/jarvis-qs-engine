# Jarvis v5.0.0-alpha.5 — Builder Adapter Dry Run, no Excel output

Scope:
- Add Builder adapter dry-run endpoint, schema, validation, trace, and plan/review summary.
- Adapter dry run uses the current BuilderRunSnapshot only.
- Block adapter dry run when snapshot is stale or clarification is pending.
- Hard-code `engine_called=false` and `excel_created=false`.
- Keep Preview/Export as safe stubs.
- Keep BAT reliability fix.

Not in scope:
- No Builder engine.
- No Formatter.
- No QA.
- No O&A.
- No formula generation.
- No workbook reading.
- No UI redesign.
- No current Jarvis replacement.
