# Alpha 22.2B Scope — Limited-Control Router Confidence Engine, no engine

Version: `v5.0.0-alpha.22.2B`

## Purpose

Alpha.22.2B allows the router confidence engine to control only low-risk no-active-task fallback/choose-tool routes.

Allowed limited-control cases:

1. General writing negative guards.
2. Generic choose-tool ambiguity.
3. Soft Builder-start shell creation.
4. Casual estimate / schedule / value / cost negative guards.

## Hard exclusions

Alpha.22.2B does not control or modify:

- pending clarification resolution
- active Builder reducer/parser grammar
- active Builder edits/actions
- attachment binding
- trade reducer mutation
- function/unit compatibility guard
- snapshot creation
- adapter dry run
- engine contract
- boundary audit / preflight / execution request
- Builder engine, workbook reading, formulas, Excel output
- Formatter, QA Checker, O&A

## Safety

The confidence engine remains side-effect free. It may choose a route only after protected contexts are excluded. It never mutates a Builder plan directly and never calls any tool engine.

Required locks:

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `contract_only=true`
- `legacy_builder_called=false`
