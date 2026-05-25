# Jarvis v5.0.0-alpha.35.3 Change Report

Scope: Conversation ID / State Path Sanitization.

## Changed

- Added `jarvis_v5/core/conversation_id_safety.py` as the shared owner for conversation ID sanitization and safe storage stems.
- Updated `ConversationStore` to sanitize accepted conversation IDs and use shared safe storage stems.
- Updated `EventLedger` to use shared safe storage stems.
- Hardened `EventLedger.list_events` to return an empty event list rather than crashing when a corrupted/non-list event payload is encountered.
- Added targeted smoke tests for malicious conversation IDs and state path safety.

## Not changed

No router, parser, workbook access, Builder engine, Formatter, QA Checker, O&A, UI, Output Center, registry execution flags, workbook metadata probe, sheet-name probe, workbook-read policy, workbook preflight, safe path resolver, or preview policy behavior was changed.
