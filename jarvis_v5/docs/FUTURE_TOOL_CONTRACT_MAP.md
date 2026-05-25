# Future Tool Contract Map — v5.0.0-alpha.35.14

All entries are contract-only and disabled.

| Tool | Capability key | Execution | Workbook read | Approval gate |
|---|---|---:|---:|---|
| Formatter | `format_workbook` | disabled | disabled | approve formatter preflight |
| QA Checker | `qa_check_boq_quantities` | disabled | disabled | approve QA mapping/tolerance |
| O&A Delta Builder | `build_omission_addition_delta` | disabled | disabled | confirm delta mode/matching |
| Bulkcheck Helper | `bulkcheck_unit_collation` | disabled | disabled | confirm target unit/levels |
| BOQ Compare | `compare_boq_versions` | disabled | disabled | confirm matching keys |
| Description / BOQ Writer | `write_boq_descriptions` | disabled | disabled | approve suggestions before writeback |
| Document Reader | `extract_qs_scope_from_documents` | disabled | disabled | approve document-read policy |
| Standards KB | `standards_reference_advisory` | disabled | disabled | confirm jurisdiction/source authority |
| Output Center | `manage_tool_outputs` | disabled | disabled | approved upstream job required |

The next phase should prepare Job Center + Output Manifest contracts, still with no execution.
