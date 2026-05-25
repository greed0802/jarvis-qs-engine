# Sheet-name Probe No-content Enforcement Plan

Future sheet-name-only probe must block:

- workbook content read
- formula read
- cell value read
- style read
- row/column dimension read
- table read
- defined name read
- hidden sheet content read
- merged cell detail read
- external link read
- Builder engine call
- Excel output

Allowed future output is limited to sheet names, sheet count, audit flags, and safety flags.

Alpha36.3 remains planning-only and keeps all read/probe flags false.


Safety lock: workbook_read=false, sheet_name_probe_allowed=false, no workbook is opened in alpha36.3.
