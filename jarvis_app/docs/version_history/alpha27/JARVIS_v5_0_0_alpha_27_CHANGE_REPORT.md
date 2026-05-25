# Jarvis v5.0.0-alpha.27 Change Report

## Version
v5.0.0-alpha.27 — Workbook Access Boundary + Preview Execution Policy, still no workbook read

## Base used
v5.0.0-alpha.26.1 — Response Schema + Test Pack Hygiene Cleanup, no behavior change

## Added
1. Metadata-only owner: `jarvis_v5/tools/builder/preview_execution_policy.py`.
2. Metadata-only endpoint: `POST /api/builder/preview-execution-policy`.
3. Request/response schemas: `PreviewExecutionPolicyRequest` and `PreviewExecutionPolicyResponse`.
4. Workbook read permission boundary policy.
5. Safe workbook path resolver policy.
6. Preview-only approval policy.
7. Export approval policy.
8. Preview result schema definition.
9. Output manifest schema definition.
10. Background job boundary plan.
11. Formula Integrity Guard connection point definition.
12. Legacy Builder failure recovery contract.
13. Alpha.27 smoke test and JSON pack.
14. Alpha.27 docs and protected boundary hash manifest.
15. QA runner known route and allowed endpoint support for the policy endpoint.

## Behavior preserved
- No chat route behavior change.
- No Builder engine connection.
- No workbook reading/parsing.
- No Formula generation.
- No Excel output.
- No Formatter, QA Checker, or O&A execution.

## Protected Builder boundary files
10 / 10 protected Builder boundary files remained unchanged.
