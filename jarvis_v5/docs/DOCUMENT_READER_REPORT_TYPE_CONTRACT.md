# Document Reader Report-Type Contract

This contract defines future document/report metadata only. It does not read documents.

## Safety

- metadata_only=true
- execution_enabled=false
- document_read=false
- ocr_enabled=false
- rag_enabled=false
- workbook_read=false
- tool_execution_called=false
- required_human_review=true
- citation/source placeholders only

## Document types

Acoustic, J1V3/JV3, BCA/NCC, Fire Engineering, Access, Stormwater, Traffic, Geotech, Arborist, DA consent/council conditions, Specifications, and Addenda/RFI logs.

## Not allowed

No parser, no OCR, no PDF read, no RAG/vector DB, no compliance/legal certification claims, no runtime Document Reader execution.
