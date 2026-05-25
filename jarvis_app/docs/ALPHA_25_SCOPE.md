# v5.0.0-alpha.25 Scope

Legacy Builder Engine Bridge Readiness Audit, still no engine.

## Purpose

Alpha.25 documents whether the current v5 Builder contract can safely bridge to the legacy Builder engine later. It is an audit/evidence build only.

## Allowed

- Version metadata update.
- Legacy Builder input inventory documentation.
- v5 Builder contract inventory documentation.
- Builder contract to legacy mapping documentation.
- Legacy bridge gap/risk audit documentation.
- Future Builder execution policy documentation.
- Protected Builder boundary hash manifest.
- Alpha.25 smoke test proving audit docs exist and safety locks stay disabled.

## Not allowed

- No Builder engine connection.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No Excel output.
- No Formatter execution.
- No QA Checker execution.
- No O&A execution.
- No snapshot/adapter/contract/preflight/execution core change.
- No registry execution flag change.
- No UI redesign.

## Build discipline

No scattered if/else patching. No duplicate route owner. One route family must have one owner. General code should consume frozen contract objects. Any future bridge work must be isolated, tested, hash-checked, and approved before touching protected Builder boundary files.
