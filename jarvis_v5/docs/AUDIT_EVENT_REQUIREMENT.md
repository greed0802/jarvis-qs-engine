# Audit Event Requirement

Future probe/execution must have an audit event contract before runtime is introduced. Alpha36.0 does not write events.

Required fields:
- event_id
- event_type
- source_route
- source_contract_id
- approval_snapshot
- permission_snapshot
- state_before
- state_after
- blocked_reason
- safety_snapshot
- timestamp_future
- actor
