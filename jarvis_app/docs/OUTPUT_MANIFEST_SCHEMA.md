# Output Manifest Schema — v1

Alpha.27 defines this schema only. It creates no output files.

Required future fields:
- `manifest_id`
- `conversation_id`
- `source_contract_id`
- `output_type`
- `status`
- `files`
- `created_at`
- `safety`

Allowed future output types:
- `builder_preview`
- `builder_export`
- `formatter_output`
- `qa_report`

File entries must use relative paths under the approved Jarvis output root and must not expose arbitrary filesystem paths.
