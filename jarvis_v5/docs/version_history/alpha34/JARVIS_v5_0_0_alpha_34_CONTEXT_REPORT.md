# JARVIS v5.0.0-alpha.34 Context Report

## Current base

v5.0.0-alpha.34 is built from v5.0.0-alpha.33.2.

## Purpose

Introduce the first controlled workbook-open boundary for sheet names only.

## Safety model

- `workbook_read=false` remains the broad content-read safety flag.
- `limited_metadata_read=true` and `sheet_names_read=true` are used only after explicit approval and only for sheet names.
- `workbook_content_read=false`, `cells_read=false`, `formulas_read=false`, and `workbook_parsed=false` remain false.
