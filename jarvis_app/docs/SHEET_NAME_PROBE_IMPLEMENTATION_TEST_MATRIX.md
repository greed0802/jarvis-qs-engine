# Sheet-name Probe Future Implementation Test Matrix

Before any real implementation can be accepted, future tests must prove:

- approval missing -> blocked
- file reference missing -> blocked
- safe path not reviewed -> blocked
- content read request -> blocked
- formula read request -> blocked
- cell value read request -> blocked
- style read request -> blocked
- Builder engine request -> blocked
- sheet-name-only approved fixture -> returns names only in a future implementation
- malicious workbook fixture -> no formula/cell/style read

Alpha36.3 only records this matrix. It does not implement the probe and does not open any workbook.


Safety lock: workbook_read=false, sheet_name_probe_allowed=false, no workbook is opened in alpha36.3.
