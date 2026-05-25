# Alpha 33.1 Scope

Version: v5.0.0-alpha.33.2
Base: v5.0.0-alpha.33

Scope: Release Artifact Test Version Hygiene, no runtime behavior change, no workbook read.

Purpose:
Fix Windows-only pytest failures caused by smoke tests comparing POSIX path strings against Windows backslash paths.

Allowed changes:
- Smoke-test path normalization only.
- Version/report/handoff metadata.

Not allowed / not touched:
- Runtime logic.
- Router.
- Parser.
- Workbook access.
- Builder engine.
- Formatter, QA, O&A.
- UI, Output Center.
- Registry execution flags.
