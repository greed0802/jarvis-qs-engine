# Chat Context Archive — v5.0.0-alpha.28

## Purpose
This archive preserves safe, user-visible Jarvis development context from the chat that approved alpha.28. It is intended to prevent practical context loss in the next chat without exposing hidden/private reasoning.

## Current continuation
The chat continued Jarvis development from the alpha.27 handoff and source ZIP. The user requested a source inventory, timeline pass, next-path dry run, governance rules, and then approved FIRE for alpha.28.

## Base/current version
- Base used: `v5.0.0-alpha.27`
- Target build: `v5.0.0-alpha.28`
- Target scope: Policy Response Hygiene + Approval Token Readiness Contract, still no workbook read

## Confirmed evidence
- Alpha.27 source ZIP was readable and extracted.
- Alpha.27 baseline pytest passed with 216 tests.
- Alpha.27 retained JSON packs passed.
- Safety aggregate remained false for workbook read, engine call, Excel creation, and legacy Builder call.
- Protected Builder boundary hash manifest passed 10/10.
- No duplicate FastAPI route was found.
- Existing duplicate top-level helper/test names were found as baseline informational findings, but no duplicate route owner was confirmed.

## Source inventory/timeline summary
The available project history showed the move from unstable v4 active Builder state and preview/export issues toward a v5 contract-first architecture. The v5 path built state, routing, reducers, snapshots, adapter dry runs, contract fixtures, boundary audits, preflight, registry, bridge-readiness probes, and finally the alpha.27 workbook access/preview execution policy checkpoint.

## Alpha.27 diagnosis
Alpha.27 was a valid policy checkpoint. It defined workbook access and preview/export execution policy, but intentionally kept all execution disabled:

- `WORKBOOK_READ_ENABLED = False`
- `BUILDER_ENGINE_EXECUTION_ENABLED = False`
- `LEGACY_BUILDER_CALLABLE = False`
- `EXCEL_OUTPUT_ENABLED = False`

Alpha.27 did not read workbooks, call the Builder engine, call legacy Builder, create preview rows, generate formulas, create Excel outputs, run Formatter, run QA, run O&A, or enqueue jobs.

## Alpha.28 dry-run decision
The next safe step was scoped as response hygiene and approval readiness only. It must not enable workbook read or execution.

## Agreed governance rules
The user reinforced:

- one route owner
- no multiple code owners for the same behavior
- one code family per patch
- batch-by-batch patching
- if Batch 0 fails, stop
- if any batch fails, stop, fix only that batch, and retest from Batch 0
- sensitive file isolation
- test/retest after every batch
- secure patch only
- deep continuity research before future handoffs
- every dry run must provide the best FIRE prompt
- every major handoff must include a Markdown chat-context archive

## Protected files and logic
Alpha.28 must not touch Builder formula/export engine, CostX formula generation, Formula Integrity Guard execution, legacy Builder execution bridge, workbook reader/parser, Excel writer/output generator, router core, slot reducer, Builder parser, Formatter, QA Checker, O&A, UI, Output Center, or background jobs.

## Known risks
- Version updates require test and pack assertion updates.
- Public policy responses should not expose raw contract/path-like metadata.
- Full UI/Windows `.bat` startup was not part of this patch scope.

## Decisions made
- Add permanent governance docs.
- Add chat-context archive.
- Keep `/api/builder/preview-execution-policy` owned by `preview_execution_policy.py`.
- Return `contract = null` in normal policy responses.
- Add public `contract_summary`.
- Add approval token/readiness metadata but do not issue tokens or execute.

## Best FIRE prompt used
The user approved FIRE for `v5.0.0-alpha.28 only: Policy Response Hygiene + Approval Token Readiness Contract, still no workbook read`, with batch-by-batch governance, protected logic exclusions, safety locks false, and final regression requirements.

## Next recommended action after alpha.28
Run a dry run for alpha.29 only. Recommended direction: Safe Workbook Path Resolver Dry Run, still no workbook open/read.
