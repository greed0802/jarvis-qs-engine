# Change Report — v5.0.0-alpha.35.15

## Base
v5.0.0-alpha.35.14

## Scope
Job Center + Output Manifest Contract, metadata only. No execution, no workbook read, no Builder engine, no Excel output.

## Added
- `jarvis_v5/schemas/job_contract_schema.py`
- `jarvis_v5/schemas/output_manifest_schema.py`
- `jarvis_v5/tests/smoke/test_alpha35_15_job_output_contract.py`
- `jarvis_v5/tests/packs/alpha35_15_job_output_contract_tests.json`
- `jarvis_v5/docs/ALPHA_35_15_SCOPE.md`
- `jarvis_v5/docs/JOB_CENTER_OUTPUT_MANIFEST_CONTRACT.md`
- `jarvis_v5/docs/ROADMAP_AFTER_ALPHA_35_14.md`

## Changed
- `jarvis_v5/config.py` version metadata only.
- registry metadata only in execution policy, capability, tool, and file requirement registries.
- retained test version assertions refreshed to current version.

## Not touched
No app/router/reducer/Builder/Formatter/QA/O&A/Document Reader/Output Center runtime files were changed. No endpoints, workers, job store runtime, output files, or download routes were added.
