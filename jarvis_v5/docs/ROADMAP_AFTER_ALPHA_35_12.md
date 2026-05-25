# Roadmap After Alpha35.12

## Current position

Jarvis now has a stable no-execution backend/advisory foundation. The next stages must remain contract-first and approval-gated.

## Roadmap gates

### alpha35.14 — Tool Contract Map, metadata only

Define contract metadata for:

- Formatter
- QA Checker
- O&A Delta Builder
- Bulkcheck Helper
- BOQ Compare
- Description / BOQ Writer
- Document Reader
- Standards KB
- Output Center

No execution.

### alpha35.15 — Job Center + Output Manifest Contract, no execution

Define job/output contracts before any long-running workbook task is enabled.

### alpha35.16 — Document Reader Report-Type Contract, no document read

Define report-type metadata and expected QS extraction targets for Acoustic, J1V3/JV3, BCA/NCC, Fire Engineering, Access, Stormwater, Geotech, Arborist, DA consent, and Specifications.

### alpha35.17 — Standards and Source Authority Registry, no compliance claim

Define source authority layers:

- statutory/code
- professional standard
- client standard
- consultant report
- drawing
- specification
- email instruction
- user assumption
- AI inference

### alpha35.18 — Workbook Read Permission Contract, still no workbook read

Define who approved read access, what file/sheet/range is allowed, and how the access is audited.

### alpha36.x — Controlled Workbook Metadata Probe

Sheet names only. No cell values, formulas, or row parsing.

### alpha37.x — Controlled Builder Preview Bridge

Preview-first, approval-gated, with Formula Integrity Guard before export.

## Do not skip

Do not connect Builder engine, workbook parsing, Formatter, QA, O&A, Document Reader, or live connectors before the relevant contract and permission gates are accepted.
