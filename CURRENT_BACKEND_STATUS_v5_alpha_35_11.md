# Current Backend Status — Jarvis v5.0.0-alpha.35.11

## Base

`v5.0.0-alpha.35.10.2` accepted runtime base, with alpha35.10.2R evidence lock as accepted proof.

## Current version

`v5.0.0-alpha.35.11 — Metadata-only Capability Advisory + QS Scope/RFI Advisor, no execution`

## Status

Built and tested as metadata-only advisory expansion.

## Safety boundary

```text
workbook_read=false
engine_called=false
excel_created=false
legacy_builder_called=false
```

## Runtime behavior added

No-active user prompts such as:

```text
What should I measure for waterproofing?
What files do I need for tiling?
What RFI should I ask for painting?
Which tool should handle old and revised BOQ comparison?
```

now route through the existing `registry_advisory_metadata_only` route and include `requirement_advisor.advisory_type`.

## Advisory types

```text
capability_advisory
qs_scope_advisory
file_requirement_advisory
rfi_template_advisory
scope_risk_advisory
```

## Not changed

- Active-task advisory was not added.
- Builder reducer/mutation paths were not touched.
- Builder formula/export engine was not touched.
- Workbook read/parse runtime was not touched.
- Preview policy was not touched.
- Formatter, QA Checker, O&A, UI, and Output Center were not touched.
