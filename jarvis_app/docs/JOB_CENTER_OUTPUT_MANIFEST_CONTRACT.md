# Job Center + Output Manifest Contract

Alpha35.15 defines schema-only contracts for future jobs and output manifests.

## Job contract
- job_id
- job_type
- source_contract_id
- source_tool_key
- approval state
- progress state
- safety envelope
- error/retry contract
- audit log contract

## Output manifest contract
- output_id
- job_id
- output_type
- filename_future
- file_path_future
- download_ref_future
- retention class
- download policy placeholder
- audit status

## Alpha35.15 blocked behavior
- no worker
- no background execution
- no job store runtime
- no output file creation
- no download routes
- no Output Center runtime
- no workbook read
