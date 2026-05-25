# Sheet-name Probe Audit Lifecycle — Future Only

Future event lifecycle:

1. `probe_requested`
2. `approval_checked`
3. `safe_path_checked`
4. `probe_started_future`
5. `probe_blocked` or `probe_completed_future`
6. `safety_snapshot_recorded`

Required future event fields:

- event_id
- event_type
- file_ref
- approval_snapshot
- permission_snapshot
- safety_snapshot
- blocked_reason
- state_before
- state_after

Alpha36.3 writes no runtime audit event and creates no event ledger.


Safety lock: workbook_read=false, sheet_name_probe_allowed=false, no workbook is opened in alpha36.3.
