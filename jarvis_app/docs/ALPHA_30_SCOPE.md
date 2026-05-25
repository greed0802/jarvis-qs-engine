# v5.0.0-alpha.30 Scope

Workbook Read Preflight Contract, still no workbook parse/output.

## Scope

- Add metadata-only workbook read preflight owner.
- Add endpoint: `POST /api/builder/workbook-read-preflight-dry-run`.
- Add schema models for preflight request/response.
- Validate workbook candidate metadata by filename extension, content type, and size metadata only.
- Reuse safe workbook path resolver metadata output without resolving or opening workbook files.
- Preserve all execution kill switches.

## Explicitly out of scope

- Workbook open/read/parse.
- Path resolving or filesystem existence checks against workbook files.
- Sheet/cell/formula reads.
- Builder engine execution.
- Legacy Builder import/call.
- Excel output.
- Formatter, QA Checker, O&A, UI, or router behavior changes.
