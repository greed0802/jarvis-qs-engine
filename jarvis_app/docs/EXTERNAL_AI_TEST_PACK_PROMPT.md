# External AI prompt for Jarvis v5 alpha.12.1 test packs

Create a valid importable JSON test pack for Jarvis v5.0.0-alpha.12.2.

Allowed endpoints only:
- POST /api/chat
- POST /api/attach
- GET /api/plan/{conversation_id}
- POST /api/builder/create-snapshot
- POST /api/builder/adapter-dry-run
- POST /api/builder/engine-contract
- GET /api/builder/engine-contract/{contract_id}
- GET /api/builder/engine-contract/latest/{conversation_id}

Rules:
- Output valid JSON only.
- Use unique `conversation_id` and `client_event_id` values.
- Always start Builder tests with `POST /api/chat` text `Build me a BOQ`.
- For `/api/attach`, do not use `json.file`. Use:
  ```json
  {
    "method": "POST",
    "endpoint": "/api/attach",
    "form": {
      "conversation_id": "...",
      "client_event_id": "...",
      "text": "Here"
    },
    "file_fixture": "Test.xlsx"
  }
  ```
- Do not call real Builder export, workbook parsing, formula generation, Formatter, QA, O&A, UI, or Excel output.
- Do not invent route names.

Known route names:
- new_builder_task_shell
- active_task_slot_edit
- active_task_slot_edit_needs_clarification
- builder_snapshot_created
- builder_snapshot_blocked
- builder_adapter_dry_run
- builder_adapter_dry_run_blocked
- builder_engine_contract_created
- builder_engine_contract_blocked
- builder_engine_contract_replay
- builder_engine_contract_latest_replay
- active_task_preview_stub
- general_stub

Use `sample_external_ai_pack_valid.json` as the model.
