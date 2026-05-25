# Jarvis v5.0.0-alpha.35.3 Bug Report

## Fixed

Malicious `conversation_id` values could be echoed and used as filesystem path stems, causing path traversal risk, Windows-invalid filename failures, and EventLedger crashes.

Examples covered:

- `../escape`
- `safe/../evil`
- `/absolute/path`
- `conv:evil`
- `quote"id`
- `CON_*`
- `nul_*`
- emoji / semicolon / spaces

## Remaining

External attack packs 004/005 still fail on `normal_id_*` expectations because Jarvis intentionally preserves safe IDs matching the approved safe ID policy. This is classified as over-strict attack-pack expectation, not a runtime bug.
