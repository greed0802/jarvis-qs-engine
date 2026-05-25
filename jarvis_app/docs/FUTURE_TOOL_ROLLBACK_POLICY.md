# Future Tool Rollback Policy

- Bulkcheck Helper: output-only rollback, source workbook untouched.
- Formatter: original workbook untouched, formatted copy only.
- QA Checker: report-only rollback, source files untouched.
- BOQ Compare: report-only rollback, source files untouched.
- O&A Delta Builder: generated workbook/report only, source files untouched.
- Document Reader: extraction report only, document untouched.
- Output Center: manifest cleanup future only, no destructive deletion by default.
- Builder Preview: preview-only, no source workbook mutation.
- Builder Export: highest risk, explicit rollback package required before enablement.
