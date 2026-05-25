# Jarvis Build Governance Rules

- Diagnose and plan first.
- Patch only the approved scope.
- Work batch by batch and stop on failures.
- Keep confirmed / likely / hypothesis separate.
- Preserve stable working logic.
- Protect Builder formula/export engine, router, parser, workbook preflight, safe path resolver, preview policy, Formatter, QA, O&A, UI, Output Center, and registry execution flags unless explicitly in scope.
- Preserve workbook_read=false, engine_called=false, excel_created=false, legacy_builder_called=false unless explicitly in scope.

# Next Chat Handoff v5 alpha.35.3

Base: v5.0.0-alpha.35.3 candidate.

What changed:

- Added shared conversation ID safety owner.
- ConversationStore and EventLedger now use safe storage stems.
- EventLedger no longer crashes on non-list event payloads.

Verification:

- Full pytest: 296 passed
- Built-in JSON packs: 40/40 passed
- Attack packs 004/005 complete without exceptions; remaining failures are safe `normal_id_*` preservation expectations.

Next recommended step:

DIAGNOSE alpha.35.3 local Windows test result.
