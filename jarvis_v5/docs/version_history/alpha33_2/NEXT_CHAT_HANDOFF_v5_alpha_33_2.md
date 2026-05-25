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

# Next Chat Handoff — v5.0.0-alpha.33.2

Current candidate: v5.0.0-alpha.33.2
Base used: v5.0.0-alpha.33.1

Purpose: Release Artifact Test Version Hygiene only.

Changed files of interest:
- `jarvis_v5/tests/smoke/test_alpha28_1_package_hygiene.py`
- `jarvis_v5/config.py` version metadata
- report/handoff/version metadata

Runtime functions changed: none.

Next step:
DIAGNOSE alpha.33.2 local Windows test result.

Do not proceed to alpha.34 until alpha.33.2 passes locally.
