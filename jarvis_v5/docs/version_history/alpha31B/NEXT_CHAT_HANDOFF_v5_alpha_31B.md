# Next Chat Handoff — v5.0.0-alpha.31B

Current version: v5.0.0-alpha.31B.
Base: v5.0.0-alpha.31A.

Latest scope: No-active generic ambiguity / prompt-injection route hygiene, no active-task behavior change, no parser behavior change, no workbook read.

What changed:

- Added no-active generic ambiguity patterns for `Do it safely.`, `Work on this attachment.`, and `What tool should use this?`.
- Added `no_active_prompt_injection_safe_block` route for no-active instruction-like unsafe text.
- Added tests and JSON pack.
- Standard packs and targeted weakness packs pass.

What did not change:

- Active-task behavior.
- Parser/conflict behavior.
- Workbook read / parse / filesystem checks.
- Builder engine / legacy Builder / Excel output.
- Formatter / QA / O&A / UI.

Next recommended dry run:

`DRY RUN v5.0.0-alpha.31C — Active non-mutating + feedback read-only ownership, no parser behavior change, no workbook read.`
