# Roadmap After Alpha 36.2

Current build: v5.0.0-alpha.36.3, Controlled Sheet-name-only Probe Implementation Plan.

Recommended next phase:

- alpha36.4: exact implementation dry run for sheet-name-only probe, still no FIRE unless confidence is high.
- alpha36.5 or later: first controlled implementation only if explicitly approved and tests prove no content/formula/cell/style read.

Do not skip from alpha36.3 directly to workbook content read or Builder engine integration.


Safety lock: workbook_read=false, sheet_name_probe_allowed=false, no workbook is opened in alpha36.3.
