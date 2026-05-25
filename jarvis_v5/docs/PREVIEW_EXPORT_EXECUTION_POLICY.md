# Preview / Export Execution Policy — v1

## Preview policy
Preview execution is disabled in alpha.27.

Future preview execution requires:
- Ready engine contract.
- Clean boundary audit.
- Preflight ready.
- Explicit user approval for preview.
- Workbook read enabled.
- Legacy Builder callable enabled.
- Execution kill switch lifted for the approved preview scope.

## Export policy
Export execution is disabled in alpha.27.

Future export requires:
- Preview completed successfully.
- Formula Integrity Guard passed.
- Explicit user approval for export.
- Excel output enabled.
- Output manifest validated.

Export must never bypass preview approval.
