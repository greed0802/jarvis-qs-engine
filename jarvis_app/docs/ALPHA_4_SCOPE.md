# Jarvis v5.0.0-alpha.4 — BuilderRunSnapshot Skeleton + BAT Reliability Fix

Scope:
- Add BuilderRunSnapshot schema/store/create/get endpoints.
- Snapshot is created from the active Builder shell plan only.
- Snapshot validation is skeleton-level: structural issues block, missing production Builder inputs warn only.
- Preview/export remain safe stubs.
- Add reliable START BAT files using `python -m uvicorn` and pause on exit.

Protected:
- No Builder engine.
- No CostX formula generation.
- No Formatter, QA, O&A.
- No workbook reading.
- No BuilderRunSnapshot execution.
- No UI redesign.
- No current Jarvis replacement.
