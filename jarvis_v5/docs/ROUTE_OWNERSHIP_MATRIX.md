# Route Ownership Matrix — v5.0.0-alpha.35.13

This evidence lock documents current route ownership to prevent duplicate route owners and scattered if/else patches.

| Route / capability family | Owner | Notes |
|---|---|---|
| No-active advisory / future tool metadata | `jarvis_v5/router/no_active_task_language_gate.py` | Advisory detection only. No execution. |
| Advisory response contract | `jarvis_v5/registry/registry_loader.py`; `jarvis_v5/schemas/registry_schema.py` | Metadata payload only. |
| Registry metadata | `jarvis_v5/registry/*.json`; `registry_loader.py` | Execution flags must remain false. |
| Active non-mutating writing/report | `jarvis_v5/router/active_task_language_gate.py` | Protect Preview false-positive guard. |
| Active feedback read-only | `jarvis_v5/router/feedback_router.py` | Feedback must not mutate Builder plan. |
| Builder setup mutation | `jarvis_v5/reducers/slot_reducer.py` | Single owner for slot edits. Not touched in alpha35.13. |
| Active action / Preview / Export shell | `active_task_action_language_gate.py` and final routing in `main_router.py` | Preview/export remain non-engine stubs. |
| Workbook read policy review | `workbook_read_policy_review.py`; `workbook_read_preflight_contract.py` | No workbook read in alpha35.13. |
| Preview execution policy | `preview_execution_policy.py` | Not touched in alpha35.13. |
| Safe workbook path resolution | `safe_workbook_path_resolver.py` | Not touched in alpha35.13. |
| Builder adapter / contract / preflight / bridge | `jarvis_v5/tools/builder/*` dedicated modules | Protected boundary. Not touched in alpha35.13. |

## Alpha35.13 rule

This build changes only version metadata, documentation, and reports. It does not add a route owner or change route behavior.
