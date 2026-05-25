# v5.0.0-alpha.19 — Contract Fixture Replay + Golden Diff Tests, no engine

## Purpose

Freeze known-good Builder engine contract shapes before any real legacy Builder import/call.

Alpha.19 adds a no-engine fixture replay/golden diff layer for saved Builder engine contract fixtures. It compares stable contract fields only and ignores volatile IDs, timestamps, local paths, hashes, and event metadata.

## Added

- `POST /api/builder/contract-fixture-replay`
- Golden diff utility: `jarvis_v5/tools/builder/contract_fixture_replay.py`
- Golden fixtures:
  - `wall_types_xgetwallarea_zone1_head2_gf_l3_contract_v1.json`
  - `reinforcement_xgetcustom_weight_t_zone1_head2_gf_l3_contract_v1.json`
- `/api/plan` visibility for latest fixture replay result
- Alpha.19 smoke tests and importable pack
- QA runner cleanup so `/api/builder/create-snapshot` top-level safety assertions are valid in alpha.18.1+

## Safety boundary

Still no Builder engine, no legacy Builder import/call, no workbook reading/parsing, no formula generation, and no Excel output.

Required safety locks remain:

```text
workbook_read=false
engine_called=false
excel_created=false
contract_only=true
legacy_builder_called=false
```

## Golden diff ignores

```text
contract_id
snapshot_id
adapter_input_id
conversation_id
task_id
active_task_id
workbook_id
attachment_id
created_at
updated_at
event_id
client_event_id
saved_path
replay_url
contract_hash
```

## Stable fields compared

```text
contract_schema_version
legacy_target
engine_version_target
engine_mode
source
contract_status
workbook_ref.filename
builder_setup.trade_profile
builder_setup.costx_function
builder_setup.custom_quantity
builder_setup.unit
builder_setup.zone_mode
builder_setup.dynamic_zones
builder_setup.heading_assignments
builder_setup.levels
builder_setup.aliases
builder_setup.item_code_settings
setup_completeness.status
setup_completeness.ready_for_future_engine
normalization.status
conflicts
validation.valid
validation.issues
validation.warnings
safety
```
