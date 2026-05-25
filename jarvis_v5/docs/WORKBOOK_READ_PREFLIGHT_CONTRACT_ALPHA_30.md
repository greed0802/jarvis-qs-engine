# Workbook Read Preflight Contract — Alpha.30

Alpha.30 adds a metadata-only dry-run contract for future workbook reading.

Owner:

- `jarvis_v5/tools/builder/workbook_read_preflight_contract.py`

Endpoint:

- `POST /api/builder/workbook-read-preflight-dry-run`

The endpoint may inspect existing Jarvis metadata store contract payloads and workbook reference metadata. It must not inspect the workbook file itself.

## Allowed metadata

- filename
- workbook_id
- attachment_id
- source
- content_type
- size_bytes
- extension
- extension policy status
- future required checks

## Forbidden actions

- `Path.resolve()` against workbook files
- `Path.exists()` against workbook files
- `Path.open()` against workbook files
- `open()` against workbook files
- `openpyxl.load_workbook`
- `pandas.read_excel`
- workbook open/read/parse
- sheet name read
- cell read
- formula read
- Builder engine call
- legacy Builder call
- Excel output

## Allowed extensions

- `.xlsx`
- `.xlsm`

## Rejected extensions

- `.pdf`
- `.zip`
- `.csv`

## Raw path scrub rule

The response must not return raw path values or forbidden exact raw path keys such as `saved_path`, `absolute_path`, `file_path`, `local_path`, `stored_path`, `resolved_path`, `raw_path`, `attachment_path`, `directory`, `parent`, `full_path`, or `path`.

Status field names such as `path_resolver_summary`, `raw_path_value_returned`, and `forbidden_path_key_returned` are allowed because they report policy state rather than exposing raw path metadata.
