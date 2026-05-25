# State Transition Contract

Allowed as metadata in alpha36.0:
- metadata_only → contract_draft
- contract_draft → approval_required
- approval_required → approval_rejected
- approval_required → metadata_probe_blocked
- approval_required → permission_revoked
- approval_required → permission_expired

Blocked in alpha36.0:
- approval_required → metadata_probe_ready_future
- metadata_only → workbook_read
- metadata_only → sheet_name_probe
- contract_draft → content_read
- approval_required → formula_read
- approval_required → Builder engine
- any state → Excel output
