# Jarvis v5.0.0-alpha.2.1 — Debug Clarification Test Endpoint + Router Trace Export

Status: parallel alpha package only.

Adds debug-only endpoints to manually test pending clarification routing and inspect router traces.

## Added
- POST /api/debug/create-test-clarification
- GET /api/debug/pending-clarification/{conversation_id}
- GET /api/debug/router-trace/{conversation_id}

## Protected / not connected
- No Builder engine
- No Formatter
- No QA Checker
- No O&A
- No slot reducer
- No zone/level parser
- No BuilderRunSnapshot
- No UI redesign
- No current Jarvis replacement
