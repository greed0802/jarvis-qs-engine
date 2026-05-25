# v5 Builder Contract Inventory

Alpha.25 inventory of the current no-engine Builder chain.

## Current safe chain

```text
Active Builder plan
→ BuilderRunSnapshot
→ Adapter dry run
→ Builder engine contract
→ Boundary audit
→ Engine preflight
→ Execution request
→ Kill switch blocks
```

## Current contract families

| v5 source | Purpose | Execution status |
|---|---|---|
| Active Builder plan | live setup shell | no engine |
| BuilderRunSnapshot | frozen approved setup state | no engine |
| Adapter dry run | normalized future engine input preview | no workbook read |
| Engine contract | stable `builder_contract_v1` payload | contract-only |
| Boundary audit | policy/safety audit of contract | no engine |
| Engine preflight | validates that execution would be blocked/ready | no engine |
| Execution request | final request object | blocked by kill switch |

## Safety fields

All Builder control responses must preserve:

```text
workbook_read=false
engine_called=false
excel_created=false
contract_only=true
legacy_builder_called=false
```

## Contract caveat

`workbook_ref` is metadata-only. It is not permission to read the workbook. Future execution must use a separate workbook-read approval gate.
