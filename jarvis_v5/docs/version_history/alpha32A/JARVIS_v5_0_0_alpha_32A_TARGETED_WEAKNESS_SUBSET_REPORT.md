# Targeted Weakness Subset Report — v5.0.0-alpha.32A

Subset: 100–109 minimal_pair_route_ownership.

Result: PASS — 500 / 500 tests.

Fixed route ownership cases:

- Preview is broken. → feedback_read_only
- Preview. → no_active_action_needs_active_task
- Use Doors and Windows. → choose_tool
- Explain safe workbook path resolver. → general help / fallback_used=false
- Run safe workbook path resolver dry run. → choose_tool / no execution
- I need a checklist for waterproofing. → general QS help / fallback_used=false

Expected old alpha.30 reference-pack result after alpha.32A if replayed unchanged: 7,700 / 8,000, with remaining 300 failures expected to be historical version-lock artifacts only.
