# Version Tag Compatibility Scan — v5.0.0-alpha.31B

## Current target
v5.0.0-alpha.31B

## Policy
Only current exact-version assertions and current release metadata are updated to v5.0.0-alpha.31B.
Historical version references under `jarvis_v5/docs/version_history/` are preserved as historical evidence.

## Updated current-version families
- `jarvis_v5/config.py` APP_VERSION.
- Smoke tests exact current-version assertions.
- JSON pack `version_target` and exact `/api/version` assertions.
- Current README/status/handoff/report files.

## Package rule
Final root package must contain only alpha.31A root release artifacts. Alpha.30.1 root artifacts are archived under `jarvis_v5/docs/version_history/alpha30_1/`.
