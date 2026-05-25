# Alpha 32C.1 Cross-file Helper Duplicate Disposition Allowlist

Version: v5.0.0-alpha.32C.1  
Base: v5.0.0-alpha.32A  
Scope: documentation / duplicate-disposition reporting only. No runtime behavior change. No workbook read.

## Final disposition wording

Cross-file helper duplicates reviewed.  
Runtime-risk duplicates: 0.  
Allowed test/local duplicates: 21.  
Allowed unrelated private duplicates: 3.  
Watchlist duplicates: 5 with documented owners.  
Must-fix duplicates: 0.

## Summary

| Classification | Count |
|---|---:|
| Total cross-file helper/function duplicates | 29 |
| Allowed test/local duplicates | 21 |
| Allowed unrelated private duplicates | 3 |
| Watchlist duplicates with documented owners | 5 |
| Must-fix duplicates | 0 |
| Runtime-risk duplicates | 0 |

## A. Allowed test/local duplicates

These duplicates live in smoke-test/test-pack helper code and do not own runtime routing, parser interpretation, workbook/path safety, execution policy, public response contracts, Builder boundary safety, or stale/default workspace behavior.

- `_assert_no_execution`
- `_chat`
- `_client`
- `_reset_data`
- `_start_builder`
- `adapter_dry_run`
- `assert_safety`
- `assert_safety_false`
- `attach_fixture`
- `attach_workbook`
- `client`
- `complete_setup`
- `complete_wall_types_setup`
- `create_snapshot`
- `create_task`
- `engine_contract`
- `post`
- `post_chat`
- `reset_data`
- `start_builder`
- `start_complete_wall_types`

Disposition: allowed test/local duplicates.

## B. Allowed unrelated private duplicates

| Helper | Disposition | Rationale |
|---|---|---|
| `_norm` | allowed unrelated private helper | Local normalization helper; no route/parser/workbook/execution ownership. |
| `_now` | allowed unrelated private helper | Timestamp helper only; no route/parser/workbook/execution ownership. |
| `now_iso` | allowed unrelated private helper | Timestamp helper only; no route/parser/workbook/execution ownership. |

## C. Watchlist duplicates with documented owners

These are not active runtime blockers. They should remain documented so future patches do not add a third owner or drift the contract.

| Helper | Future owner | Reason |
|---|---|---|
| `_blocked_by_policy` | future shared policy reason helper | Used by bridge/policy families; keep ownership explicit before consolidation. |
| `_contract_payload` | future contract serialization utility | Similar payload conversion pattern; consolidate only if safe later. |
| `_public_workbook_ref` | future workbook reference public-view helper | Alpha.33 must avoid creating a third workbook-reference formatter. |
| `canonical_hash` | future schema/core hash utility | Same stable hashing concept across schema families. |
| `_word_pattern` | future shared alias-pattern helper | Parser/registry alias matching concept; change only with parser tests. |

## D. Must-fix duplicates

None.

## Alpha.33 guardrails

Alpha.33 workbook metadata probe planning is not blocked by the duplicate disposition, provided it does not:

- enable workbook read,
- add a new workbook-reference formatter,
- duplicate policy-block helper behavior,
- mutate Builder plan state from metadata alone,
- touch Builder engine, Formatter, QA, O&A, UI, or Output Center.

## Protected systems

This disposition does not require changes to protected Builder boundary files. It is an allowlist/reporting closure only.
