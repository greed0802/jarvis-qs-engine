# Alpha 30.1 — 8,000-Test Weakness Triage

Version: v5.0.0-alpha.30.1
Base: v5.0.0-alpha.30
Scope: Weakness Pack Triage + Route/Response Compatibility Plan, no behavior change.

## Source result

The reference-informed weakness suite was run against alpha.30 before this triage build. It contained 160 packs and 8,000 tests.

| Metric | Result |
|---|---:|
| Total packs | 160 |
| Total tests | 8000 |
| Passed tests | 5985 |
| Failed tests | 2015 |
| Passed packs | 54 |
| Failed packs | 106 |
| Error packs | 0 |

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```

Confirmed: the weakness pack found route/response/readiness gaps, but did not breach workbook read, engine, Excel, or legacy Builder safety locks.

## Failed focus families

| Focus | Passed | Failed | Failed packs | Packs | Examples |
|---|---:|---:|---:|---:|---|
| `mixed_reference_red_team` | 2040 | 510 | 51 | 51 | 110_mixed_reference_red_team_110.json, 111_mixed_reference_red_team_111.json, 112_mixed_reference_red_team_112.json |
| `prompt_injection_no_active_no_execution` | 0 | 300 | 6 | 6 | 084_prompt_injection_no_active_no_execution_1.json, 085_prompt_injection_no_active_no_execution_2.json, 086_prompt_injection_no_active_no_execution_3.json |
| `plan_state_after_contract_persistence` | 0 | 250 | 5 | 5 | 090_plan_state_after_contract_persistence_1.json, 091_plan_state_after_contract_persistence_2.json, 092_plan_state_after_contract_persistence_3.json |
| `active_feedback_read_only` | 0 | 200 | 4 | 4 | 031_active_feedback_read_only_1.json, 032_active_feedback_read_only_2.json, 033_active_feedback_read_only_3.json |
| `minimal_pair_route_ownership` | 300 | 200 | 10 | 10 | 100_minimal_pair_route_ownership_1.json, 101_minimal_pair_route_ownership_2.json, 102_minimal_pair_route_ownership_3.json |
| `preview_export_policy_excessive_agency_block` | 0 | 200 | 4 | 4 | 066_preview_export_policy_excessive_agency_block_1.json, 067_preview_export_policy_excessive_agency_block_2.json, 068_preview_export_policy_excessive_agency_block_3.json |
| `active_non_mutating_state_first` | 75 | 175 | 5 | 5 | 020_active_non_mutating_state_first_1.json, 021_active_non_mutating_state_first_2.json, 022_active_non_mutating_state_first_3.json |
| `generic_choose_tool_ambiguity` | 175 | 75 | 5 | 5 | 015_generic_choose_tool_ambiguity_1.json, 016_generic_choose_tool_ambiguity_2.json, 017_generic_choose_tool_ambiguity_3.json |
| `pending_clarification_blocks_actions` | 200 | 50 | 5 | 5 | 035_pending_clarification_blocks_actions_1.json, 036_pending_clarification_blocks_actions_2.json, 037_pending_clarification_blocks_actions_3.json |
| `active_action_language_owner` | 270 | 30 | 6 | 6 | 025_active_action_language_owner_1.json, 026_active_action_language_owner_2.json, 027_active_action_language_owner_3.json |
| `function_unit_conflict_raw_canonical` | 225 | 25 | 5 | 5 | 041_function_unit_conflict_raw_canonical_1.json, 042_function_unit_conflict_raw_canonical_2.json, 043_function_unit_conflict_raw_canonical_3.json |

## Classification

### Real route/readiness weaknesses

- `generic_choose_tool_ambiguity`: no-active generic tool-like prompts still fall to `general_stub` in some cases.
- `active_non_mutating_state_first`: active-task explanatory/help text is still too narrow.
- `active_feedback_read_only`: issue-report language can be captured by active routes before feedback ownership wins.
- `pending_clarification_blocks_actions`: risky action aliases have phrase gaps while clarification is pending.

### Response-shape compatibility gaps

- `plan_state_after_contract_persistence`: the pack expects alias fields such as `version`, `latest_snapshot`, `latest_adapter`, and `latest_engine_contract` on `/api/plan`.
- `preview_export_policy_excessive_agency_block`: the pack expects some alias names such as `workbook_read_permission_boundary.workbook_read_enabled`; current alpha.30 uses `enabled=false`.

### Parser-sensitive future risk

- `function_unit_conflict_raw_canonical`: function/unit raw/canonical alias conflicts need a dedicated parser/conflict-guard dry run. Do not bundle with router or response compatibility.

### Safety-pass but route-hygiene failure

- `prompt_injection_no_active_no_execution` and mixed red-team packs did not trigger execution, but expected stronger no-fallback/tool-selection behavior.

## Responsible code families

| Family | Files/functions |
|---|---|
| No-active generic ambiguity | `jarvis_v5/router/no_active_task_language_gate.py`, `jarvis_v5/router/main_router.py`, `detect_generic_tool_ambiguity(...)` |
| Active non-mutating | `jarvis_v5/router/active_task_language_gate.py`, `jarvis_v5/router/engineering_language_gate.py`, `is_active_task_non_mutating_language(...)` |
| Feedback read-only | `jarvis_v5/router/feedback_router.py`, `jarvis_v5/router/main_router.py`, `is_active_task_issue_feedback(...)`, `handle_feedback(...)` |
| Clarification action block | `jarvis_v5/router/clarification_gate.py`, `jarvis_v5/router/action_aliases.py`, `jarvis_v5/router/active_task_action_language_gate.py` |
| Response aliases | `jarvis_v5/app.py::api_plan(...)`, `jarvis_v5/tools/builder/preview_execution_policy.py` |
| Parser conflict aliases | `jarvis_v5/parsers/trade_parser.py`, `jarvis_v5/parsers/conflict_guard.py` |

## What not to patch together

Do not combine router ownership fixes, response compatibility aliases, clarification-action phrases, and parser conflict-guard aliasing in one patch. Each should be isolated with its own dry run and pack subset.

## Alpha 30.1 decision

Alpha 30.1 intentionally changes no runtime route/parser/policy behavior. It preserves the weakness findings as first-class project evidence and defines the next safe patch sequence.
