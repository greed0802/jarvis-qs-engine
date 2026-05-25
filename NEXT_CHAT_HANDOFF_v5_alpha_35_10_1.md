# Next Chat Handoff — v5.0.0-alpha.35.10.1

Use `v5.0.0-alpha.35.10.1` as the candidate package for local verification.

Base / rollback: `v5.0.0-alpha.35.10` built-in pack hygiene accepted regression checkpoint.

Scope fixed: UAE phrase `Levels B3 to B1, GF, Podium, Level 1 to Level 20` no longer creates an unnecessary basement-order clarification. Snapshot and adapter dry-run can proceed contract-only.

Tests already passed in sandbox: pytest 335, alpha35.10.1 targeted pack 3/3, external QS curriculum pack 15 50/50, focused-v3 quick packs 026 and 060 50/50.

Recommended local verification next:

1. Run pytest.
2. Run alpha35.10.1 targeted pack.
3. Run external Phase 1 replay. Expected non-version result should improve by 5 tests; pack 15 should pass 50/50.
4. Optionally create alpha35.10.1 focused-v3 pack or accept version-lock differences from alpha35.10 focused-v3.

Do not touch Builder formula/export engine, workbook access/read behavior, Formatter, QA, O&A, UI, Output Center, preview policy, registry execution flags, safe path resolver, workbook policy, snapshot endpoint logic, adapter endpoint logic, or Builder engine unless explicitly approved.
