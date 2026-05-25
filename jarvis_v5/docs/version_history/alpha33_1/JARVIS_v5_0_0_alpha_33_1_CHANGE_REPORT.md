# Jarvis v5.0.0-alpha.33.1 Change Report

## Base
v5.0.0-alpha.33

## Scope
Windows Path Normalization Test Hygiene, no runtime behavior change, no workbook read.

## Changed
- Normalized smoke-test owner scan paths with `Path.relative_to(...).as_posix()`.
- Updated version/report/handoff metadata to v5.0.0-alpha.33.1.
- Archived alpha.33 root artifacts under `jarvis_v5/docs/version_history/alpha33/`.

## Runtime changes
None, except version/app metadata in `jarvis_v5/config.py`.

## No behavior changes
No router, parser, workbook access, Builder engine, Formatter, QA, O&A, UI, Output Center, or registry execution behavior changed.
