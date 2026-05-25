# Legacy Bridge Shadow Probe Contract — v5.0.0-alpha.26

## Endpoint

`POST /api/builder/legacy-bridge-shadow-probe`

## Request

```json
{
  "conversation_id": "alpha26_probe",
  "client_event_id": "a26_probe_001",
  "contract_id": null,
  "allow_missing_contract": true
}
```

## Response contract

The route is always metadata-only and blocked for execution.

```json
{
  "route": "builder_legacy_bridge_shadow_probe",
  "metadata_only": true,
  "execution_enabled": false,
  "blocked": true,
  "workbook_read": false,
  "engine_called": false,
  "excel_created": false,
  "legacy_builder_called": false,
  "bridge_probe": {
    "bridge_layer_found": true,
    "bridge_layer_status": "stub_only",
    "legacy_import_attempted": false,
    "legacy_module_imported": false,
    "legacy_callable_available": false,
    "contract_found": true,
    "contract_ready": true,
    "safe_for_future_mapping": true,
    "safe_for_execution": false
  },
  "blocked_by_policy": [
    "workbook_read_disabled",
    "legacy_builder_callable_disabled",
    "excel_output_disabled",
    "execution_kill_switch"
  ]
}
```

## Allowed metadata sources

- Current config execution locks.
- Existing saved contract metadata, if available.
- Static presence of the v5 legacy bridge stub file.

## Blocked operations

- Do not import the real legacy Builder runtime.
- Do not call the legacy Builder.
- Do not open workbook files.
- Do not parse workbook contents.
- Do not generate formulas.
- Do not create preview rows.
- Do not create Excel.
