# v5.0.0-alpha.22.2A — Router Confidence Engine Shadow Mode + No-Task Plan Safety, no engine

## Purpose

Add a read-only Router Confidence Engine that scores what route Jarvis would choose, without changing the current router decision.

## Included

- `jarvis_v5/router/router_confidence_engine.py`
- `confidence_engine` metadata on `/api/chat` responses
- `/api/plan` no-active-task and conversation-not-found safety/readiness envelope
- Shadow-mode tests and QA pack

## Confidence engine metadata

Each `/api/chat` response includes:

- `actual_route`
- `would_route`
- `would_confidence`
- `route_mismatch`
- `confidence_reason`
- `tool_candidates`
- `negative_guard`
- `requires_clarification`
- `control_taken=false`

## Safety

No route replacement was added. No reducer, Builder engine, workbook reader, formula generator, Excel writer, Formatter, QA Checker, O&A, or UI redesign is connected.
