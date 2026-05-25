# Sheet-name Probe Permission Sequence — Future Only

A future sheet-name-only probe must require all of the following before any file access:

1. `permission_request_id` exists.
2. `file_ref` exists and points to one approved workbook reference.
3. `approval_state=approved_sheet_name_probe_future`.
4. `content_read_approved=false`.
5. `formula_read=false`.
6. `cell_value_read=false`.
7. `style_read=false`.
8. safe path review completed.
9. audit event contract exists.

Approval for sheet names must never imply permission to read workbook content, formulas, cell values, styles, or Builder data.

Alpha36.3 does not approve or run any probe.


Safety lock: workbook_read=false, sheet_name_probe_allowed=false, no workbook is opened in alpha36.3.
