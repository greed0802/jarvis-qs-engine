# IMPORTANT — JARVIS BUILD GOVERNANCE

Before doing anything:
- Identify latest approved base.
- DIAGNOSE/DRY RUN/FIRE must be followed exactly.
- Do not patch/build/package unless user explicitly says FIRE.
- Check hashes, changed files, changed functions, tests, errors, duplicates, owners, route families, and protected boundaries.
- Use batch-by-batch isolated sandbox work.
- Stop on errors.
- Report confirmed / likely / hypothesis separately.
- Protect Builder formula/export engine, workbook access, Formatter, QA, O&A, UI, Output Center, and registry execution flags unless explicitly in scope.

# Jarvis v5.0.0-alpha.33.1 Procedure Report

Batch 0 — Baseline inventory/hash/test evidence.
Batch 1 — alpha28.1 test path normalization.
Batch 2 — alpha29 test path normalization.
Batch 3 — alpha30 test path normalization.
Batch 4 — alpha33 test path normalization.
Batch 5 — targeted failed-test rerun.
Batch 6 — full smoke regression in chunks due sandbox timeout.
Batch 7 — built-in JSON pack sweep.
Batch 8 — reports/handoff/context/procedure/change/test reports.
Batch 9 — hygiene clean/package.

A timed/chunked run encountered stale runtime data from previous partial runs; runtime data was cleaned and the affected chunks passed.
