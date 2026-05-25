# Jarvis v5.0.0-alpha.35.10.1 Test Report

## Commands run

- `python -m compileall -q jarvis_v5`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q`
- `python run_alpha_smoke_tests.py --pack jarvis_v5/tests/packs/alpha35_10_1_uae_podium_basement_level_tests.json --no-report`
- `python run_alpha_smoke_tests.py --pack /mnt/data/external_phase1/jarvis_qs_senior_1000_test_curriculum/packs/15_multinational_floor_level_language.json --no-report`
- Focused v3 quick safety checks: packs 026 and 060.

## Results

- compileall: PASS
- pytest: 335 passed
- alpha35.10.1 targeted pack: PASS, 3 / 3
- external QS senior curriculum pack 15: PASS, 50 / 50
- focused v3 quick pack 026: PASS, 50 / 50
- focused v3 quick pack 060: PASS, 50 / 50

## Safety aggregate

All targeted and diagnostic pack checks kept:

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## Not run / limitation

Full focused-v3 3,000 replay was not completed in the sandbox window for alpha.35.10.1. The accepted alpha.35.10 focused-v3 baseline remains the rollback/safety checkpoint; local full replay is recommended after extracting this package.
