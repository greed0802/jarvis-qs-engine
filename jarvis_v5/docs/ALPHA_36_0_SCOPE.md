# Alpha36.0 Scope — Pre-Execution Integrity Matrix + State Transition Contract

Version: `v5.0.0-alpha.36.0`  
Base: `v5.0.0-alpha.35.19`

Scope is metadata only. No workbook read, no sheet-name probe, no worker, no Builder engine, no Excel output.

Included:
- execution tier matrix
- tool risk tier matrix
- state transition contract
- approval escalation contract
- blocked transition list
- audit event requirement
- rollback policy per future tool
- readiness gates before sheet-name-only probe

Excluded:
- workbook reader runtime
- permission store runtime
- endpoints
- sheet-name probe
- worker/job/output runtime
- workbook content/formula/cell read
- Builder/Formatter/QA/O&A/Document Reader/Output Center runtime
