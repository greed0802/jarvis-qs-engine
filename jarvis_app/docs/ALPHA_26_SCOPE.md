# v5.0.0-alpha.26 Scope

Legacy Builder Bridge Shadow Import / Readiness Probe, no workbook read.

## Purpose

Alpha.26 adds a metadata-only readiness probe for the future legacy Builder bridge.
It answers whether the current v5 contract metadata and locked execution policies are ready for future bridge mapping review.

## Added

- `POST /api/builder/legacy-bridge-shadow-probe`
- Isolated owner: `jarvis_v5/tools/builder/legacy_bridge_shadow_probe.py`
- Request/response schema for the probe.
- QA runner endpoint and route awareness.
- Alpha.26 smoke tests and JSON test pack.
- Alpha.26 protected boundary hash manifest.

## Hard safety boundaries

- No Builder engine call.
- No legacy Builder import/call.
- No workbook reading/parsing.
- No formula generation.
- No preview row generation.
- No Excel output.
- No Formatter, QA Checker, or O&A execution.
- No UI redesign.

## Build discipline

- No scattered if/else patching.
- One bridge responsibility = one owner.
- `app.py` only exposes the endpoint wrapper.
- The probe owner owns probe logic.
- Protected Builder boundary files stay unchanged.
