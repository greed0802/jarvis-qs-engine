# Chat Context Archive — v5.0.0-alpha.31B

User requested alpha.31A after alpha.30.1 weakness triage. The build is scoped to response-shape compatibility only.

Important decisions:
- Add aliases, do not rename/remove existing fields.
- `plan_mutated=false` must not hide true mutations; true values and changed slots win.
- Version updates require drift scan and current-version-only assertion updates.
- Targeted weakness subset must be exact; mixed red-team route failures stay deferred.
