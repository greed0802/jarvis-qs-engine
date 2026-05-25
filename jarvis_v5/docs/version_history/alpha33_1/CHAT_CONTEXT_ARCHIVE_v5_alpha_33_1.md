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

# Chat Context Archive — v5.0.0-alpha.33.1

alpha.33.1 was requested after local Windows pytest showed 4 failed owner-scan tests due path separator differences.
The patch is test-only and uses `.as_posix()` for relative path comparisons.
