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

Candidate build: v5.0.0-alpha.35.3 — Conversation ID / State Path Sanitization.
Base: v5.0.0-alpha.35 candidate.
Last accepted official base before local pass: v5.0.0-alpha.34.

Changes: TestPackExecutor close/context support; /api/dev/run-smoke-tests closes executor; alpha12 direct runner test context-managed; run_alpha_smoke_tests.py Unicode-safe output.

Next required action: DIAGNOSE alpha.35.3 local Windows test result.
If local pytest passes and policy endpoint remains safe, accept alpha.35.3. Then plan alpha.35.3 malicious conversation_id/path sanitization.
