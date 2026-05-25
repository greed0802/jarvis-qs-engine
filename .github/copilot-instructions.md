# Jarvis Copilot Instructions

You are working inside the Jarvis QS Engineering System.

This system is a deterministic Quantity Surveying engine.

---

## HARD RULES

You must NEVER:
- modify quantity calculation logic without explicit request
- change Builder/export outputs
- break Excel/BOQ formatting structure
- merge parser and builder logic
- remove QA or validation steps
- rewrite architecture without permission

---

## CORE SYSTEMS (PROTECTED)

Treat these as locked:

- builder/
- parser/
- workflow/
- export logic
- formula engine

Any changes here must be minimal and incremental only.

---

## DEVELOPMENT RULE

Always prefer:
- small edits
- isolated functions
- test-driven changes
- backward compatibility

Never do full rewrites.

---

## WORK STYLE

When unsure:
- ask for clarification
- do not guess business logic
- do not invent QS rules

---

## JARVIS PURPOSE

Jarvis is NOT a chatbot.

It is a:
- QS automation engine
- BOQ processor
- quantity validation system
- Excel export system

Accuracy is more important than speed.
