# Future Builder Execution Policy

Alpha.25 defines the future policy only. It does not enable execution.

## Required future gates

Before any real Builder preview/export can run:

1. Current Builder contract exists.
2. Snapshot is current.
3. Adapter is current.
4. Boundary audit is clean.
5. Engine preflight is ready.
6. No pending clarification exists.
7. Workbook-read flag is explicitly enabled.
8. Legacy Builder callable flag is explicitly enabled.
9. Excel output flag is explicitly enabled.
10. User gives explicit approval for preview/export.
11. Output manifest path is prepared.
12. Formula integrity checks are defined for the selected mode.

## Current alpha.25 flags

```text
BUILDER_ENGINE_EXECUTION_ENABLED=false
LEGACY_BUILDER_CALLABLE=false
WORKBOOK_READ_ENABLED=false
EXCEL_OUTPUT_ENABLED=false
```

## Preview/export split

Preview should be enabled before export. Export should require a successful preview and a separate explicit approval.
