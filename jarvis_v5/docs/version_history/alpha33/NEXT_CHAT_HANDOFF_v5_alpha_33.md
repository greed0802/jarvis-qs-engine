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

# Next Chat Handoff — v5.0.0-alpha.33

Current version: v5.0.0-alpha.33
Base: v5.0.0-alpha.32C.1

What changed:
- Added Workbook Metadata Probe Approval Contract.
- Added POST /api/builder/workbook-metadata-probe-approval.
- Added single owner module: jarvis_v5/tools/builder/workbook_metadata_probe_approval.py.
- Added schemas, QA runner route support, smoke tests, JSON pack, reports.

What stayed locked:
- No workbook open/read/parse.
- No sheet-name/cell/formula reading.
- No Builder engine.
- No legacy Builder.
- No Excel output.
- No Formatter/QA/O&A/UI/Output Center changes.

Recommended next step:
DRY RUN v5.0.0-alpha.34 — Sheet Name Probe Approval Contract, if required, still no cells/formulas/engine/output.
