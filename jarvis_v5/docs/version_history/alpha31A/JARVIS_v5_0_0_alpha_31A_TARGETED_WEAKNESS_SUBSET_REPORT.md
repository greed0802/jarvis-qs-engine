# Jarvis v5.0.0-alpha.31B Targeted Weakness Subset Report

## Scope
Response-shape compatibility only. Router/parser failures are out of scope.

## Exact adjusted full packs run
- 066–069 preview_export_policy_excessive_agency_block: 4 / 4 packs passed, 200 / 200 tests passed.
- 090–094 plan_state_after_contract_persistence: 5 / 5 packs passed, 250 / 250 tests passed.

Version assertions in the external alpha.30 weakness packs were adjusted to the current alpha.31A version for compatibility measurement only.

## Filtered mixed red-team check
Representative mixed red-team pack 110 was run for plan_mutated path-presence measurement only. It had 0 `$.plan_mutated` path-not-found failures. Remaining route mismatches stay deferred to alpha.31B/31C.

## Result
Targeted response-shape subset: 9 / 9 packs passed, 450 / 450 tests passed.
