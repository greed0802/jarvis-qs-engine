# v5.0.0-alpha.10 — Builder Engine Contract Adapter, still no Excel output

## Goal

Add a formal contract payload that describes exactly what a future Builder engine would receive, without calling the engine.

## In scope

- Builder engine contract schema
- Contract adapter from current BuilderRunSnapshot / adapter dry run
- `POST /api/builder/engine-contract`
- Contract validation
- Contract status in `/api/plan`
- Contract status in Review
- Router trace/debug proof
- Smoke tests

## Out of scope

- Builder engine
- Workbook reading/parsing
- Sheet inspection
- CostX formula generation
- Excel preview/output
- Formatter
- QA Checker
- O&A
- UI redesign
- Current Jarvis replacement

## Safety proof required

Every successful or blocked contract response must keep:

```text
workbook_read=false
engine_called=false
excel_created=false
contract_only=true
legacy_builder_called=false
```

## Contract creation blocks when

- No active Builder task exists
- Pending clarification exists
- Snapshot is missing/stale/mismatched
- Adapter dry run is stale
- Setup completeness is not ready for future engine
- Required setup slots are missing
- Normalization requires clarification
- Conflicts are unresolved
