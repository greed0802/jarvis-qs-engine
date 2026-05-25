# Pre-Execution Integrity Matrix

Alpha36.0 defines execution law only. Tier 0/1 may exist as metadata. Tier 2+ remain future-only and blocked.

| Tier | Name | Alpha36.0 status | Examples |
|---:|---|---|---|
| 0 | Advisory / metadata only | allowed as metadata | advisory, source authority |
| 1 | Permission / approval contract | allowed as metadata | workbook permission contract |
| 2 | Metadata probe | blocked future | sheet-name-only probe |
| 3 | Read-only extraction | blocked future | document extraction |
| 4 | Deterministic calculation | blocked future | Bulkcheck, QA, BOQ Compare |
| 5 | Output generation | blocked future | O&A reports/workbooks |
| 6 | Workbook modification / preview | blocked future | Formatter, Builder preview bridge |
| 7 | Builder formula/export | blocked future | Builder export engine |

All tiers keep workbook_read=false, sheet_name_probe_allowed=false, engine_called=false, excel_created=false.
