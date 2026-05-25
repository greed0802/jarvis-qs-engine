# Safe Workbook Path Resolver Dry Run — Alpha.29

Owner: `jarvis_v5/tools/builder/safe_workbook_path_resolver.py`

Endpoint: `POST /api/builder/safe-workbook-path-resolver-dry-run`

Purpose:

- inspect contract/workbook_ref metadata already stored by Jarvis
- detect whether raw path-like metadata exists internally
- return public workbook metadata only
- prove no raw path values or forbidden exact raw path keys are returned

Allowed public workbook metadata:

- filename
- workbook_id
- attachment_id
- source
- content_type
- size_bytes

Forbidden exact raw path keys in normal response:

- saved_path
- absolute_path
- file_path
- local_path
- stored_path
- resolved_path
- raw_path
- attachment_path
- directory
- parent
- full_path
- path

Safety fields must remain false:

- path_resolved
- filesystem_checked
- workbook_filesystem_checked
- workbook_opened
- workbook_read
- engine_called
- excel_created
- legacy_builder_called
