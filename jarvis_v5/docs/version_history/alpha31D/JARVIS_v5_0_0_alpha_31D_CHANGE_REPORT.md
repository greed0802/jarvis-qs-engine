# Change Report — v5.0.0-alpha.31D

Base: v5.0.0-alpha.31C
Version: v5.0.0-alpha.31D

Scope: Pending clarification risky-action phrase coverage, no parser behavior change, no workbook read.

## Changed

- Added pending-only `_detect_pending_risky_action_text(...)` in `jarvis_v5/router/clarification_gate.py`.
- Added `run_builder` to pending clarification risky-action blocking only.
- Updated version metadata and scope docs.
- Added alpha.31D smoke test and JSON pack.

## Fixed

- `Run builder now` is blocked while pending clarification is open.

## Preserved

- Existing Preview/Export/Download/Approve-preview pending clarification blocks.
- Review remains allowed while pending clarification is open.
- Valid clarification answers still resolve.
- Cancel, cancel task, and start-new remain functional.
- Parser behavior unchanged.
- Workbook/engine/Excel/legacy execution remains disabled.
