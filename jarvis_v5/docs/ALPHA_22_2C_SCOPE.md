# Alpha.22.2C Scope

Version: `v5.0.0-alpha.22.2C`

Title: **Router Language Ownership Cleanup + Active Setup Grammar Normalization, no engine**

## Goal

Fix the router-language ownership conflicts found after alpha.22.2B, then add active Builder setup grammar normalization without touching any engine or execution path.

## Included

1. One no-active-task language gate for:
   - writing help
   - casual non-tool guard
   - generic choose-tool ambiguity
   - soft Builder shell creation
2. One Builder shell creation helper.
3. Shared no-active-task language classification for router and confidence engine.
4. Stable public `negative_guard` categories with separate debug detail.
5. No-active-task language coverage expansion inside the shared gate only.
6. Active Builder setup text normalizer before parser dispatch.
7. Raw + canonical conflict checks before mutation.
8. Focused smoke and JSON pack tests for route ownership and active setup normalization.

## Excluded / protected

- Builder engine
- Legacy Builder import/call
- Workbook reading/parsing
- Formula generation
- Excel output
- Formatter
- QA Checker
- O&A
- Snapshot creation logic
- Adapter dry run logic
- Engine contract logic
- Boundary audit
- Preflight
- Execution request
- UI redesign
- Current v4 rollback

## Expected route ownership

Protected contexts remain first:

1. Pending clarification
2. Attachment binding
3. Active task action/edit/reducer
4. Feedback
5. No-active-task language gate
6. Final fallback

No-active-task phrases should use:

```text
router_step = no_active_task_language_gate
```

Active Builder setup phrases should use:

```text
router_step = slot_reducer
confidence_engine.control_taken = false
```
