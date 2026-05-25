# v5.0.0-alpha.26.1 Scope

Response Schema + Test Pack Hygiene Cleanup, no behavior change.

## Scope

- Add standard no-engine safety envelope to debug clarification response schema/output.
- Document/support test pack format discriminator for multi-step packs.
- Update retained test pack version targets/assertions to v5.0.0-alpha.27.
- Reorder engine-contract latest route before contract-id replay route for readability only.
- Keep `/api/chat` response model unchanged; no response-shape behavior change was accepted for this build.

## Safety

- No Builder engine.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter, QA Checker, or O&A.
- No protected Builder boundary file changes.
