# Legacy Builder Bridge Gap Audit

## Current state

The v5 backend can create and validate a no-engine Builder contract, but the legacy Builder execution bridge is intentionally disabled.

## Blocking gaps before future execution

1. Real workbook-read permission boundary.
2. Safe workbook path/handle resolver.
3. Legacy Builder function signature confirmation.
4. Preview result schema.
5. Export result / output manifest schema.
6. Formula Integrity Guard integration point.
7. Failure recovery and rollback contract.
8. Background job / timeout handling boundary.
9. Approval policy for preview versus export.
10. Test fixture proving contract-to-preview behavior without corrupting workbook formulas.

## Protected files likely involved later

Future bridge work may require touching:

```text
jarvis_v5/tools/builder/legacy_engine_bridge.py
jarvis_v5/tools/builder/engine_preflight.py
jarvis_v5/tools/builder/engine_contract_adapter.py
jarvis_v5/core/engine_execution_store.py
jarvis_v5/core/engine_preflight_store.py
```

Those files remain untouched in alpha.25.

## Recommendation

Next technical bridge should still be shadow/import readiness only, not actual Excel output.
