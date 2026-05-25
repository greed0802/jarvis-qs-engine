# v5.0.0-alpha.12 — Local QA Test Runner + Importable Test Packs, no engine

## Scope

Adds a local API test runner so alpha safety flows can be tested without manual Swagger copy/paste.

## Added

- `jarvis_v5/qa_runner/` local test runner modules.
- Built-in test pack: `jarvis_v5/tests/packs/alpha11_contract_negative_guards.json`.
- Importable JSON test-pack support.
- JSON-path style assertions.
- Local JSON/Markdown test reports under `jarvis_v5/data/test_reports/`.
- Dev endpoint: `POST /api/dev/run-smoke-tests`.
- CLI: `python run_alpha_smoke_tests.py`.

## Safety locks

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `contract_only=true`
- `legacy_builder_called=false`

## Not connected

No Builder engine, workbook reading/parsing, formula generation, Excel output, Formatter, QA, O&A, UI redesign, or current Jarvis replacement.
