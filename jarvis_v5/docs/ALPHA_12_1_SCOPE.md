# v5.0.0-alpha.12.1 — Test Pack Import Guard + Fixture Attach Support, no engine

Scope: harden the local QA test runner so imported AI-generated JSON packs fail clearly and safely.

Added:
- Structured invalid-pack handling for missing packs, bad JSON, and bad schema.
- `file_fixture` support for `/api/attach` steps using `jarvis_v5/tests/fixtures/Test.xlsx`.
- Preflight compatibility validation endpoint: `POST /api/dev/validate-test-pack`.
- Compatibility warnings for `json.file` attach misuse, unknown expected routes, endpoint-specific safety assertions, and contract-created expectations without setup steps.
- Better path-not-found diagnostics with available top-level response fields and hints.
- Sample valid external AI test pack.

Safety preserved:
- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `contract_only=true`
- `legacy_builder_called=false`

No Builder engine, workbook reading/parsing, formula generation, Excel output, Formatter, QA, O&A, UI redesign, or current Jarvis replacement.
