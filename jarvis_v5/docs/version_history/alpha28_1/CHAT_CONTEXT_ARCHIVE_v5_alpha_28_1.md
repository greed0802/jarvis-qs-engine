# Chat Context Archive — v5.0.0-alpha.28.1

This archive preserves safe user-visible context for the alpha.28.1 cleanup build.

## Decision

The user questioned why alpha.28 did not clean stale root artifacts and asked about existing baseline duplicates. The agreed correction was to create alpha.28.1 as a cleanup-only package hygiene build before alpha.29.

## Scope agreed

- Use alpha.28 as base.
- Clean alpha.27 and alpha.28 root release artifacts from final alpha.28.1 ZIP root.
- Archive older artifacts under `jarvis_v5/docs/version_history/alpha27/` and `jarvis_v5/docs/version_history/alpha28/`.
- Add duplicate scan report and package hygiene report.
- Add package hygiene tests.
- Keep helper duplicates audit-only.
- No runtime behavior change.

## Explicitly avoided

- helper renames unless tests absolutely require it
- preview policy behavior changes
- schema behavior changes
- router changes
- Builder engine/workbook/Excel execution
- Formatter, QA, O&A, UI, Output Center changes

## Safety principle

This was a release hygiene patch only. Cross-file helper duplicates are documented and deferred; duplicate FastAPI routes and same-file duplicate definitions remain clean.


## Build result summary

Alpha.28.1 completed as cleanup-only. Tests passed: pytest 225, JSON packs 27 / 27, JSON tests 116 / 116. Safety aggregate remained false for workbook read, engine call, Excel creation, and legacy Builder call.
