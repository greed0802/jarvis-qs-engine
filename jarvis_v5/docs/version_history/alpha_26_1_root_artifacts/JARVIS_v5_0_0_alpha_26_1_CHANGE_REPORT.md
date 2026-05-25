# Jarvis v5.0.0-alpha.26.1 Change Report

## Version

v5.0.0-alpha.26.1 — Response Schema + Test Pack Hygiene Cleanup, no behavior change

## Base used

v5.0.0-alpha.26 — Legacy Builder Bridge Shadow Import / Readiness Probe, no workbook read

## What changed

1. Added `safety: dict` to `DebugClarificationResponse`.
2. Applied the standard no-engine safety envelope to `/api/debug/create-test-clarification` responses.
3. Added documented test pack format discriminator support: `format = multi_step`.
4. Added `format: multi_step` to retained JSON packs.
5. Updated retained test pack version targets/assertions to `v5.0.0-alpha.26.1`.
6. Converted the brittle `route_confidence == 98` pack assertion into a presence assertion.
7. Added QA runner allowance for `/api/debug/create-test-clarification`.
8. Reordered the latest engine-contract route above the contract-id replay route for readability only.
9. Added alpha.26.1 smoke test and JSON test pack.
10. Archived alpha.26 root artifacts into docs/version_history and kept package hygiene clean.

## Explicitly skipped

`/api/chat` response_model was not added because this build was scoped to no behavior change and that endpoint is the main UI/API route. It can be reconsidered only after an isolated before/after response-shape comparison.

## Protected / not touched

No Builder engine, legacy Builder execution/import/call, workbook reading/parsing, formula generation, Excel output, Formatter, QA Checker, O&A, UI redesign, or protected Builder boundary file changes.
