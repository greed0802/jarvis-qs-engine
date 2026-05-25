# v5.0.0-alpha.5.1 — Adapter Dry Run Freshness + Plan Display Polish

## Scope

- Mark/display previous adapter dry-run as stale when its source BuilderRunSnapshot becomes stale.
- Show adapter freshness/status in `/api/plan`, Review, and router trace.
- Keep adapter dry-run endpoint blocking stale snapshots.
- Keep `engine_called=false` and `excel_created=false`.
- Keep Preview/Export as safe stubs.

## Excluded

- No Builder engine.
- No Formatter.
- No QA.
- No O&A.
- No formula generation.
- No workbook reading.
- No UI redesign.
- No current Jarvis replacement.
