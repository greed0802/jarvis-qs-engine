# Manual API Test Checklist — v5.0.0-alpha.24.2

Use Swagger at `/docs`.

## 1. Version

GET `/api/version`

Expected: `version = v5.0.0-alpha.24.2`, Builder execution disabled, workbook read disabled, Excel output disabled.

## 2. Builder shell

POST `/api/chat`

```json
{"conversation_id":"manual_alpha24_2","client_event_id":"m001","text":"Build me a BOQ","mode":"ask_first"}
```

Expected: `route = new_builder_task_shell`, `fallback_used=false`, route context present.

## 3. Active action language

POST `/api/chat` with same conversation and unique event IDs:

- `Please review the current setup` → `active_task_review`
- `Preview it please` → `active_task_preview_stub`
- `Export it when ready` → `active_task_export_stub`
- `Download the output` → `active_task_action_stub`

Expected: no engine call, no Excel output, no workbook read.

## 4. Setup edits

- `The unit should be m2, not no` → `active_task_slot_edit`
- `Please put Old and New under Zone 1` → `active_task_slot_edit`
- `Head 2 should be for Zone 1` → `active_task_slot_edit`

Expected: mutation only through slot reducer.

## 5. Registry advisory

POST `/api/chat` in a new conversation:

```json
{"conversation_id":"manual_alpha24_2_registry","client_event_id":"r001","text":"Create a BOQ checklist from fire report","mode":"ask_first"}
```

Expected: `registry_advisory_metadata_only`, `metadata_only=true`, `execution_enabled=false`.

## 6. Execution request

POST `/api/builder/engine-execution-request`

Expected: blocked by kill switch; no workbook read, no engine call, no Excel output.
