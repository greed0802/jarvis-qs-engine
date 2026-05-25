# Jarvis Build Governance Rules

- Diagnose and plan first.
- Patch only the approved scope.
- Work batch by batch and stop on failures.
- Protect Builder formula/export engine, workbook access behavior, Formatter, QA, O&A, UI, Output Center, and registry execution flags unless explicitly in scope.
- Keep confirmed / likely / hypothesis separate.

# Handoff

Version: v5.0.0-alpha.35.3.
Base: v5.0.0-alpha.35.2.
Scope: No-active workbook-read policy/content-read route ownership.
Result: sandbox full pytest passed; built-in JSON packs passed; attack packs 006-008 passed; 009-011 no longer fallback/start Builder but retain expected-route conflicts.
Next recommended action: local Windows test, then diagnose active-task policy routing families 014-023.
