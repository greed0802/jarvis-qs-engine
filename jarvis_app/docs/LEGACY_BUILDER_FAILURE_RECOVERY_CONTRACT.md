# Legacy Builder Failure Recovery Contract — v1

Alpha.27 defines this contract for later use. It does not call the legacy Builder.

Future failure routes:
- `builder_preview_execution_failed`
- `builder_export_execution_failed`

Recovery rules:
- Preserve active plan and contract.
- Do not mark preview/export ready.
- Quarantine partial output files.
- Surface safe user message and detailed debug evidence.
- Require rerun after correction.
