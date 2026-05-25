# Blocked Transition List

Minimum blocked transitions:
- metadata_only → sheet_name_probe
- metadata_only → workbook_content_read
- metadata_only → formula_read
- metadata_only → cell_value_read
- metadata_only → Builder engine
- metadata_only → Excel output
- approval_required → workbook_read
- metadata_permission_approval → workbook_content_read
- sheet_name_probe_approval_future → content_read
- content_read_approval_future → Builder engine
- any state → legacy_builder_called
- any state → registry execution flag true
