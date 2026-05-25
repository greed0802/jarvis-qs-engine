# Jarvis v5.0.0-alpha.3 — Slot Reducer Skeleton

Status: parallel v5 rewrite package only.

## Scope

- Adds typed Builder shell plan mutation through the slot reducer only.
- Supports narrow explicit patterns for:
  - zone set
  - zone append
  - zone replace
  - ambiguous zone replace clarification
  - level set
  - trade/function/unit state stubs
- Keeps Review/Preview/Export safe stubs.
- Keeps feedback read-only and duplicate event guard.

## Not included

- No Builder engine.
- No Formatter.
- No QA Checker.
- No O&A.
- No BuilderRunSnapshot.
- No formula generation.
- No workbook reading.
- No UI redesign.
- No current Jarvis replacement.

## Package hygiene

Old alpha BAT files and version reports were moved into:

`docs/version_history/JARVIS_v5_alpha_1_to_2_2_reports.zip`

The package root now keeps only the current alpha.3 starter and reports.
