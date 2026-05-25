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

# Next Chat Handoff — v5.0.0-alpha.33.1

Current accepted candidate: v5.0.0-alpha.33.1
Base: v5.0.0-alpha.33

What changed:
- Test-only Windows path normalization in smoke owner scans.
- Version/report/handoff metadata updated.

What did not change:
- No runtime logic.
- No router/parser/workbook/engine/Formatter/QA/O&A/UI/Output Center change.
- No registry execution flag change.

Next recommended action:
DIAGNOSE alpha.33.1 local Windows pytest result.

After local alpha.33.1 passes, return to REVIEW/DRY RUN alpha.34 Sheet Name Probe Approval Contract.
