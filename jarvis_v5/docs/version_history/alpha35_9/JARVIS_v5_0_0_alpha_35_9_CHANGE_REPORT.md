# JARVIS v5.0.0-alpha.35.10 Change Report

## Base

v5.0.0-alpha.35.8

## Scope

Pending Clarification Policy/Action Ownership, no execution, no workbook read.

## Changed

- Added pending-only workbook content/open/preflight blocking while clarification is open.
- Allowed explicit workbook-read policy review while pending clarification as read-only, with pending clarification preserved.
- Guarded trade_profile_requires_clarification so unrelated text cannot resolve it.
- Added Joinery/Painting-only smoke tests and alpha35.9 JSON pack.

## Not touched

No Builder engine, workbook read, workbook open behavior, parser, Formatter, QA, O&A, UI, Output Center, safe path resolver, preview policy, registry execution flags, workbook preflight behavior outside pending clarification, or Builder formula/export engine.
