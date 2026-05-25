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

# NEXT CHAT HANDOFF — v5.0.0-alpha.35.3

Current approved build candidate: v5.0.0-alpha.35.3, pending user local test acceptance.

Base used: v5.0.0-alpha.34.

Scope: Workbook Read Policy Review, policy/contract only. No workbook content read.

Next recommended step after local acceptance:
DRY RUN v5.0.0-alpha.36 — Workbook Structure Probe Approval Contract, structure/sheet existence only, no cells, no formulas, no Builder engine, no Excel output.
