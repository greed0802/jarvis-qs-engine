# Alpha 30.1 — Weakness Patch Sequence

Base evidence: 8,000-test reference-informed weakness pack against alpha.30.

## Required sequence

1. **alpha.31A — Response-shape compatibility only**
   - Add backward-compatible aliases for `/api/plan` and preview/export policy response expectations.
   - No router behavior changes.
   - No parser changes.
   - No workbook read.

2. **alpha.31B — No-active generic ambiguity / prompt-injection route hygiene**
   - Strengthen no-active tool ambiguity and prompt-injection route ownership.
   - Preserve execution locks.
   - Do not touch active-task reducer/parser.

3. **alpha.31C — Active non-mutating + feedback read-only ownership**
   - Ensure active explanations/help and issue reports route to the correct non-mutating/read-only owners.
   - Do not mutate Builder setup.

4. **alpha.31E — Pending clarification risky-action phrase coverage**
   - Expand risky action phrases while preserving Review as allowed.
   - Do not touch parser or Builder engine.

5. **alpha.31E or alpha.32 — Parser function/unit conflict alias consolidation**
   - Dedicated parser/conflict-guard dry run only.
   - Sensitive because it touches Builder setup interpretation.

## Deferred

- Cross-file helper duplicates remain documented only.
- Dormant-code registry remains protected.
- Workbook probing/parsing remains deferred until route/response weaknesses are triaged.
