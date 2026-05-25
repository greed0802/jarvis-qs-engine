# Alpha.31A Targeted Weakness Subset

Alpha.31A only measures response-shape compatibility. It does not require route/parser weakness families to pass.

## Full packs included
- 066_preview_export_policy_excessive_agency_block_1
- 067_preview_export_policy_excessive_agency_block_2
- 068_preview_export_policy_excessive_agency_block_3
- 069_preview_export_policy_excessive_agency_block_4
- 090_plan_state_after_contract_persistence_1
- 091_plan_state_after_contract_persistence_2
- 092_plan_state_after_contract_persistence_3
- 093_plan_state_after_contract_persistence_4
- 094_plan_state_after_contract_persistence_5

## Filtered measurement only
Mixed red-team packs may be checked only for plan_mutated path-presence improvement. Their route mismatches remain deferred.

## Deferred weakness families
- generic no-active ambiguity
- prompt-injection route hygiene
- active non-mutating route ownership
- feedback read-only route ownership
- pending clarification action phrase coverage
- parser function/unit conflict aliases
