# Next Chat Handoff — Jarvis v5.0.0-alpha.35.11

## Accepted base used

`v5.0.0-alpha.35.10.2` with alpha35.10.2R accepted proof.

## New package

`v5.0.0-alpha.35.11 — Metadata-only Capability Advisory + QS Scope/RFI Advisor, no execution`

## What changed

- Registry metadata was enriched for capability/future-tool advisory, QS scope, file requirements, RFI templates, and scope-risk checklist.
- `requirement_check()` now returns advisory contract fields:
  - `advisory_type`
  - `advisory_route`
  - `builder_mutation_allowed=false`
  - `active_task_mutated=false`
  - `requires_file_read=false`
- Narrow no-active advisory patterns were added for:
  - what should I measure for
  - what files do I need for
  - what RFI should I ask/raise
  - which tool/capability should handle
- Existing `registry_advisory_metadata_only` route is reused.
- No new route family was created.
- Active-task advisory was not included.

## Safety proof to preserve

```text
workbook_read=false
engine_called=false
excel_created=false
legacy_builder_called=false
```

## Tests run

- `python -m compileall -q jarvis_v5`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`
- `python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_11_capability_advisory_tests.json`
- `python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_10_2_active_writing_report_preview_false_positive_tests.json`

## Suggested next step

Run a broader no-active advisory weakness pack before considering active-task advisory support. Keep active-task advisory deferred unless confidence stays above 95%.
