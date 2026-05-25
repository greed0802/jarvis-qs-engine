# Fallback Audit Instructions — v5.0.0-alpha.25

Use this checklist before accepting a rollback candidate.

## Required audit checks

1. `active_task=true` should not route to `general_stub`.
2. `fallback_used=true` cases must be reviewed by family.
3. `registry_advisory_metadata_only` must remain metadata-only.
4. `execution_enabled=true` must not appear in registry JSON files.
5. Builder control endpoints must keep no-engine safety fields false.
6. Protected Builder boundary file hashes must match the manifest.

## Failure triage

Classify each failure as:

- valid route coverage gap
- old-pack version drift
- response-shape drift
- unsupported future feature expectation
- intentional blocked/safe behavior

Do not patch by phrase unless the phrase maps cleanly into an existing route family.
