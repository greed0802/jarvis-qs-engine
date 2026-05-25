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

# Jarvis v5.0.0-alpha.33.1 Context Report

Current official build after approval: v5.0.0-alpha.33.1.

Base: v5.0.0-alpha.33.

Reason for build: local Windows test hygiene after user reported 4 pytest failures and 271 passes.

No workbook, engine, parser, router, UI, Formatter, QA, O&A, Output Center, or registry execution change was in scope.
