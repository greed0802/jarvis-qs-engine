# Sheet-name Probe Dry-run Patch Map

Alpha36.2 is diagnostic only. Future implementation, if separately approved, should be isolated from Builder and routed through a dedicated workbook metadata probe module.

Future candidate owner, not created in this build:

```text
jarvis_v5/tools/workbook_metadata_probe/sheet_name_probe_contract.py
jarvis_v5/tools/workbook_metadata_probe/sheet_name_probe_dry_run.py
jarvis_v5/tools/workbook_metadata_probe/sheet_name_probe_safety.py
```

No runtime file is created in alpha36.2.

Protected no-touch files remain:
- `jarvis_v5/app.py`
- all router files
- `jarvis_v5/registry/registry_loader.py`
- `jarvis_v5/tools/builder/*.py`
- workbook policy runtime
- safe path resolver
- Builder formula/export engine
