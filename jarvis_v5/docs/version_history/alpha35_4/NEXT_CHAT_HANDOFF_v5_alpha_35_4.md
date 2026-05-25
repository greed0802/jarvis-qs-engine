# Jarvis Build Governance Rules

- Diagnose and plan first.
- Do not patch/build/package unless FIRE is approved.
- Record baseline hashes, protected Builder boundary hashes, changed files, route/owner duplicates, tests, and safety aggregate for every build.
- Work batch by batch in isolated sandbox.
- Stop if a batch fails unless the failure is understood and fixed within approved scope.
- Do not touch protected Builder formula/export engine, parser, workbook access, Formatter, QA, O&A, UI, Output Center, or registry execution flags unless explicitly in scope.

# Handoff — v5.0.0-alpha.35.5

Base: v5.0.0-alpha.35.3.1.
Scope: no-active sheet-name probe ambiguity route ownership.

Changed:
- `jarvis_v5/router/no_active_task_language_gate.py`
- `jarvis_v5/tests/smoke/test_alpha35_5_no_active_sheet_name_probe_ambiguity.py`
- version/report metadata

Result:
- attack 012-013 pass
- attack 006-008 still pass
- attack 009-011 remain only route-expectation conflict, no fallback/Builder shell
- safety aggregate false

Next recommended step: DIAGNOSE alpha.35.4 local Windows test result.
