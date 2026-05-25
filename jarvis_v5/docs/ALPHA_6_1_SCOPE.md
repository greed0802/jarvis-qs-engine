# v5.0.0-alpha.6.1 — Attachment Directory Creation + Error-safe Upload Response

Scope:
- Ensure `data/attachments` exists before saving uploads.
- Return safe JSON for attachment save failures instead of raw 500.
- Preserve task state when upload save fails.
- Keep `workbook_read=false` safety proof.

Not included:
- No workbook reading/parsing.
- No Builder engine.
- No Formatter, QA, O&A.
- No formula generation.
- No UI redesign.
