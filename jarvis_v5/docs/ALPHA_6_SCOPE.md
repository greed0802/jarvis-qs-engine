# v5.0.0-alpha.6 — Attachment Binding + Workbook Reference Snapshot

## Scope

- Bind uploaded workbook metadata to the active Builder task.
- Store workbook metadata in conversation state via `active_workbook_id`.
- Capture `workbook_ref` inside BuilderRunSnapshot.
- Pass `workbook_ref` into Builder Adapter Dry Run input.
- Show workbook metadata in `/api/plan`, Review, and router trace.
- Add `workbook_read=false` safety proof.

## Safety boundary

No workbook reading, sheet inspection, Excel parsing, Builder engine, Formula engine, Formatter, QA Checker, O&A, Preview engine, Export engine, or UI redesign.

## Expected validation behavior

Attaching a workbook removes the snapshot/adapter warning `No workbook attached`, but the alpha may still warn about missing trade/profile, CostX function, unit, heading assignments, or levels.
