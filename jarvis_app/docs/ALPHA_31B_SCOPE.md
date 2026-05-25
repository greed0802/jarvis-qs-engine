# v5.0.0-alpha.31B Scope

Scope: No-active generic ambiguity / prompt-injection route hygiene, no active-task behavior change, no parser behavior change, no workbook read.

## Included

- Add narrow no-active generic choose-tool coverage for:
  - `Do it safely.`
  - `Work on this attachment.`
  - `What tool should use this?`
- Add no-active prompt-injection safe-block route for instruction-like requests that attempt to override safety, reveal raw paths/system prompt, call workbook readers, run Builder engine/legacy Builder, create Excel, or delete outputs.
- Add tests and retained JSON pack.
- Preserve all execution locks.

## Excluded

- Active-task non-mutating / feedback route fixes.
- Pending clarification action phrase coverage.
- Parser/function-unit conflict alias changes.
- Workbook read, Builder engine, legacy Builder, Excel output, Formatter, QA, O&A, UI.
