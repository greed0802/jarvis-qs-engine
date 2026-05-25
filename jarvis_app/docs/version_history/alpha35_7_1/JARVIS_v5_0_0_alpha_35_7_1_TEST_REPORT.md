# Jarvis v5.0.0-alpha.35.7.1 Test Report

Generated: 2026-05-19T10:26:40.523326+00:00

## Test commands

```text
python -m compileall -q jarvis_v5
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q
```

## Results

```text
PASS - compileall
PASS - pytest
315 passed in 18.16s
```

## Targeted pack replay

```text
003_policy_future_tier_strict_all_disabled: PASS 50/50
029_workbook_read_preflight_strict_block_1: PASS 50/50
030_workbook_read_preflight_strict_block_2: PASS 50/50
031_workbook_read_preflight_strict_block_3: PASS 50/50
040_registry_poisoning_cannot_enable_read_1: PASS 50/50
041_registry_poisoning_cannot_enable_read_2: PASS 50/50
042_registry_poisoning_cannot_enable_read_3: PASS 50/50
043_registry_poisoning_cannot_enable_read_4: PASS 50/50
044_registry_endpoint_strict_no_execution_1: PASS 50/50
045_registry_endpoint_strict_no_execution_2: PASS 50/50
046_registry_endpoint_strict_no_execution_3: PASS 50/50
047_registry_endpoint_strict_no_execution_4: PASS 50/50
060_mixed_focused_attack_60: expected partial 40/50
```

## Pack 060 note

The remaining 10 failures are the known sheet-name strict expectations only:

- `workbook_opened expected false, got true`
- `sheet_names_read expected false, got true`

This behavior was intentionally out of scope for alpha.35.7.1.

## Safety aggregate

All targeted packs kept:

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```
