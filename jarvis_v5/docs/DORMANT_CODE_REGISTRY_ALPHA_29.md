# Dormant Code Registry — Alpha.29

Dormant code is not automatically useless code. The following items are reserved or watchlist items and must not be deleted due to lost context.

## Reserved

### `jarvis_v5/schemas/clarification_schema.py`

Future purpose: typed clarification model for active-task questions, pending clarification state, clarification replies, blocked actions, and review/preview/export guards.

Future owner/family: active-task clarification, Builder setup clarification, router clarification guard, pending action blocker.

Deletion protection: do not delete unless a newer clarification schema fully replaces it and tests prove all clarification routes use the new owner.

### `jarvis_v5/schemas/tool_result_schema.py`

Future purpose: unified tool result schema for Builder, Formatter, QA Checker, O&A, BOQ Writer, Output Center, and future tool registry outputs.

Future owner/family: Output Center, Tool Registry, Formatter result, QA result, O&A result, Builder preview/export result.

Deletion protection: do not delete unless Output Center has a confirmed replacement result schema.

### `get_registry_item()`

Future purpose: single capability/tool lookup from the Global Capability Registry.

Future owner/family: Tool Registry, Capability Registry, QS Scope Advisor, future tool metadata lookup.

Deletion protection: do not delete unless registry loader has a replacement single-item lookup API.

### `safe_workbook_path_resolver_policy()`

Future purpose: static policy description for safe workbook path resolving before real workbook access is enabled.

Future owner/family: preview execution policy, safe workbook path resolver, workbook access boundary.

Deletion protection: do not delete while workbook access boundary is still being staged.

## Reserved / watchlist

### `summarize_builder_plan()`

Future purpose: human-readable Builder setup summary for Review Setup, handoff, debug reports, support logs, and active task snapshots.

Future owner/family: Builder Review, BuilderRunSnapshot, debug export, chat setup preview.

Deletion protection: do not delete during cleanup-only or resolver patches. Review only when Builder review/snapshot summary ownership is redesigned.

### `format_setup_completeness_lines()`

Future purpose: readable setup completeness output showing missing fields, ready fields, blocked fields, and next required user action.

Future owner/family: Builder setup completeness, Review Setup, clarification gate, preview readiness, export readiness.

Deletion protection: do not delete unless setup completeness formatting is fully owned by another documented function/module.

### Preview/output/background policy helpers

Future purpose: define future boundaries for preview result schema, export output manifest, background job execution, Formula Integrity Guard connection, and execution recovery.

Future owner/family: Builder preview, Builder export, Output Center, background job runner, Formula Integrity Guard handoff.

Deletion protection: do not delete unless future execution policy is replaced by a documented equivalent module.
