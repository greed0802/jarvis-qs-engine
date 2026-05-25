# Jarvis v5.0.0-alpha.35.11 Change Report

## Version

`v5.0.0-alpha.35.11 — Metadata-only Capability Advisory + QS Scope/RFI Advisor, no execution`

## Base used

`v5.0.0-alpha.35.10.2 — Active Writing/Report Preview False-positive Guard, no workbook read, no engine`

## Scope

Metadata-only advisory expansion. No active-task advisory route was added.

## Runtime/source changes

- `jarvis_v5/config.py`
  - Updated app version to `v5.0.0-alpha.35.11`.
- `jarvis_v5/registry/capability_registry.json`
  - Added/enriched metadata-only capability entries for future-tool advisory, capability clarification, QS scope advice, file requirement advice, RFI template advice, and scope-risk checklist.
- `jarvis_v5/registry/tool_registry.json`
  - Added metadata-only tool entries for future tool advisor, QS scope advisor, file requirement advisor, RFI template advisor, and scope risk advisor.
- `jarvis_v5/registry/scope_advisor_registry.json`
  - Added more QS scope advisor metadata for doors/windows, glazing, plasterboard, ceilings, floor finishes, joinery, roofing, fire stopping, and acoustic treatments.
- `jarvis_v5/registry/file_requirement_registry.json`
  - Added advisory file categories such as door/window schedule, room data sheet, acoustic report, fire engineering report, access report, J1V3/JV3 report, DA consent conditions, addenda/RFI log, current BOQ, revised BOQ, and CostX/Cubit export.
- `jarvis_v5/registry/rfi_template_registry.json`
  - Added RFI templates for levels/locations, inclusions/exclusions, drawing/spec conflicts, report recommendations, testing/commissioning, and builder/services interface.
- `jarvis_v5/registry/requirement_advisor_registry.json`
  - Added requirement metadata for what-to-measure, file requirements, RFI drafting, future-tool choice, and scope-risk checklist.
- `jarvis_v5/registry/registry_loader.py`
  - Added metadata-only `advisory_type` / `advisory_route` contract values:
    - `capability_advisory`
    - `qs_scope_advisory`
    - `file_requirement_advisory`
    - `rfi_template_advisory`
    - `scope_risk_advisory`
  - Added `builder_mutation_allowed=false`, `active_task_mutated=false`, and `requires_file_read=false` to advisory responses.
- `jarvis_v5/router/no_active_task_language_gate.py`
  - Added narrow no-active advisory route patterns only.
  - Reused existing `registry_advisory_metadata_only` route.
- `jarvis_v5/schemas/registry_schema.py`
  - Added advisory contract fields to the registry requirement-check response schema.

## Test changes

- Added `jarvis_v5/tests/smoke/test_alpha35_11_capability_advisory.py`.
- Added `jarvis_v5/tests/packs/alpha35_11_capability_advisory_tests.json`.
- Updated retained test version targets/expectations to `v5.0.0-alpha.35.11` so the full pytest suite remains current-version clean.

## Docs / handoff

- Added `jarvis_v5/docs/ALPHA_35_11_SCOPE.md`.
- Added `CURRENT_BACKEND_STATUS_v5_alpha_35_11.md`.
- Added `NEXT_CHAT_HANDOFF_v5_alpha_35_11.md`.
- Added alpha35.11 start scripts.

## Protected / not touched

- No Builder formula/export engine change.
- No workbook content read/parse change.
- No Builder engine change.
- No Formatter change.
- No QA Checker change.
- No O&A change.
- No UI change.
- No Output Center change.
- No preview policy change.
- No safe path resolver change.
- No workbook policy runtime change.
- No Builder reducer/mutation path change.
- No registry execution flag changed to true.

## Safety boundary

```text
workbook_read=false
engine_called=false
excel_created=false
legacy_builder_called=false
```
