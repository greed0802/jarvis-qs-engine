# Sheet-name Probe Implementation Blueprint — Future Only

This document describes the future implementation sequence. It is not executable in alpha36.3.

Future sequence:

1. User requests sheet-name-only metadata probe.
2. Route identifies a probe request without mutating Builder state.
3. Permission contract is checked.
4. Explicit sheet-name-only approval is verified.
5. File reference is checked.
6. Safe path review is completed.
7. Future probe opens only the workbook container enough to list sheet names.
8. No cell values, formulas, styles, dimensions, hidden contents, tables, named ranges, or external links are read.
9. Audit event is emitted.
10. Result returns sheet names and safety flags only.

Alpha36.3 status:

- implemented=false
- runtime_called=false
- workbook_read=false
- sheet_name_probe_allowed=false
