IMPORTANT — JARVIS BUILD GOVERNANCE

Before doing anything:
- Identify latest approved base.
- DIAGNOSE/DRY RUN/FIRE must be followed exactly.
- Do not patch/build/package unless user explicitly says FIRE.
- Check hashes, changed files, changed functions, tests, errors, duplicates, owners, route families, and protected boundaries.
- Use batch-by-batch isolated sandbox work.
- Stop on errors.
- Report confirmed / likely / hypothesis separately.
- Protect Builder formula/export engine, workbook access, Formatter, QA, O&A, UI, Output Center, and registry execution flags unless explicitly in scope.

# Jarvis v5.0.0-alpha.33.2 Procedure Report

Batch 0 — baseline inventory/hash/protected boundary: completed.
Batch 1 — package hygiene smoke test expected artifact update: completed.
Batch 2 — targeted artifact test rerun: passed.
Batch 3 — compile/full smoke retest: compile passed; monolithic pytest timed out in sandbox, clean file chunks passed 275/275.
Batch 4 — built-in JSON pack sweep: 38/38 packs, 174/174 tests passed.
Batch 5 — reports/handoff/context/change/test reports: completed.
Batch 6 — hygiene clean/package: completed.

No batch failure required a runtime patch.
