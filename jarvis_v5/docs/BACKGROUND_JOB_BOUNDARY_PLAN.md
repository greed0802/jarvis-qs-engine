# Background Job Boundary Plan — v1

Alpha.27 does not enqueue background jobs.

Future job execution requires:
- `job_id`
- `conversation_id`
- `contract_id`
- `job_type`
- `approval_token`
- `created_at`
- `status`
- `safety`

Rules:
- Job failure must not mutate the active Builder plan.
- Partial outputs are quarantined until validated.
- Failed preview/export produces support-log evidence.
- Background workbook read remains blocked until explicitly approved.
