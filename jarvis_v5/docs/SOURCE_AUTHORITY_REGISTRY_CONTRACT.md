# Source Authority Registry Contract — v5.0.0-alpha.35.17

All source authority entries are metadata-only and cannot certify compliance.

Required flags:

```text
metadata_only=true
execution_enabled=false
document_read=false
ocr_enabled=false
rag_enabled=false
web_lookup_enabled=false
standards_ingestion_enabled=false
workbook_read=false
can_claim_compliance=false
can_certify_compliance=false
requires_human_review=true
```

## Authority hierarchy

- statutory_code
- professional_standard
- client_standard
- consultant_report
- specification / project specification
- drawing_note
- council_condition
- addendum
- rfi_response
- user_assumption
- ai_inference

AI inference is the lowest authority and must be treated as a hypothesis. User assumptions must be labelled as assumptions, not confirmed project facts.

Jarvis may use sources to inform BOQ scope, risks, and RFI prompts. Jarvis must not make legal, statutory, professional, client, or consultant compliance certification claims.
