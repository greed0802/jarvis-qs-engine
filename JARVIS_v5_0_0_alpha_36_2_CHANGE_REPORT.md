# Change Report — v5.0.0-alpha.36.2

Base: `v5.0.0-alpha.36.1`

Scope: Sheet-name-only Metadata Probe Dry Run, diagnostic/evidence only.

## Files changed

Runtime metadata:
- `jarvis_v5/config.py`

Docs/evidence:
- `jarvis_v5/docs/ALPHA_36_2_SCOPE.md`
- `jarvis_v5/docs/SHEET_NAME_PROBE_DRY_RUN_PATCH_MAP.md`
- `jarvis_v5/docs/SHEET_NAME_PROBE_FUTURE_BOUNDARY_REVIEW.md`
- `jarvis_v5/docs/SHEET_NAME_PROBE_NO_READ_SAFETY_REVIEW.md`
- `jarvis_v5/docs/ROADMAP_AFTER_ALPHA_36_1.md`

Tests:
- `jarvis_v5/tests/smoke/test_alpha36_2_sheet_name_probe_dry_run.py`
- `jarvis_v5/tests/packs/alpha36_2_sheet_name_probe_dry_run_tests.json`

## Functions changed

No production function logic changed. No route, endpoint, registry loader, workbook reader, permission store, sheet-name probe, safe path resolver, Builder, Formatter, QA, O&A, Document Reader, or Output Center runtime changed.

## Added

Dry-run evidence for future sheet-name-only probe boundaries, no-read safety, future patch map, and blocked behavior.
