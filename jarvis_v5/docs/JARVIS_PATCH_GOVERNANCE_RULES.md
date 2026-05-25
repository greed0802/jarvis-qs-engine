# Jarvis Patch Governance Rules

These rules must be followed for every Jarvis DIAGNOSE, DRY RUN, REVIEW, FIRE, and HANDOFF.

Jarvis must prioritize stability, evidence, isolation, and secure incremental patching over speed.

---

## 1. Evidence First

Before planning or patching, identify:

- current version
- base version
- source files available
- readable files
- missing or expired files
- exact issue or target scope
- affected route/code family
- protected logic that must not be touched

Never present a hypothesis as confirmed.

Use:

- Confirmed = directly proven by source, logs, tests, debug exports, or reproducible behavior
- Likely = strongly supported but not fully proven
- Hypothesis = possible cause needing verification

---

## 2. No Patch Without Approval

Do not patch, build, package, or modify project files unless the user explicitly says:

- FIRE
- proceed
- approved
- clearly approves the build/patch

DIAGNOSE, PLAN, REVIEW, and DRY RUN are read-only.

---

## 3. One Route Owner Rule

Every route family must have one clear owner.

Do not allow multiple modules to independently decide the same route behavior.

For every patch, identify the owner of:

- route decision
- state mutation
- schema/response shape
- execution policy
- tests

If duplicate ownership is found, stop and resolve ownership before adding new behavior.

---

## 4. One Code Family Per Patch

Each patch must touch only one code family unless explicitly approved.

Examples of separate code families:

- router
- active task state
- slot reducer
- Builder setup parser
- Builder policy endpoint
- Builder engine bridge
- workbook access
- Formatter
- QA Checker
- O&A
- UI
- Output Center
- docs/tests only

Do not mix unrelated fixes into one build.

---

## 5. Batch-by-Batch Patch Rule

Every build must be split into batches.

Each batch must have:

- purpose
- allowed files
- disallowed files
- exact changes
- tests after the batch
- stop condition

If Batch 0 fails, do not proceed.

If any batch fails:

1. Stop.
2. Fix only that batch.
3. Retest.
4. Rerun from Batch 0 before continuing.

No skipping failed gates.

---

## 6. Batch 0 Baseline Lock

Every FIRE must start with a no-change baseline check.

Minimum Batch 0 checks:

- compile check
- pytest
- JSON pack runner
- safety aggregate
- execution flag scan
- duplicate route scan
- protected file/hash check when relevant

If baseline is not clean, do not patch.

---

## 7. Sensitive File Isolation

Sensitive files must not be touched unless they are directly in scope and explicitly approved.

Sensitive areas include:

- Builder formula/export engine
- CostX formula generation
- Formula Integrity Guard
- legacy Builder bridge
- workbook reader/parser
- Excel writer/output generator
- router core
- slot reducer
- Builder parser
- snapshot/contract/preflight stores
- Formatter engine
- QA Checker engine
- O&A engine
- Output Center

Touching a sensitive file requires:

- exact reason
- exact function affected
- regression tests
- rollback note
- confidence statement

---

## 8. Execution Safety Locks

Do not enable these unless the build scope explicitly approves execution:

```python
WORKBOOK_READ_ENABLED = False
BUILDER_ENGINE_EXECUTION_ENABLED = False
LEGACY_BUILDER_CALLABLE = False
EXCEL_OUTPUT_ENABLED = False
```

No hidden workbook open.

No hidden legacy Builder import/call.

No hidden Excel save.

No hidden background job enqueue.

No old experimental v4 logic may be mixed into v5 unless explicitly approved.

---

## 9. Preview-First / Approval-First Rule

Builder workflow must remain:

```text
metadata
→ contract
→ dry run
→ readiness
→ preview
→ user approval
→ export
```

Export must require:

- successful preview
- Formula Integrity Guard pass when enabled
- explicit export approval
- output manifest
- safe output handling

---

## 10. Protected QS Logic

Never damage or silently normalize protected QS content.

Protect:

- CostX formulas
- live Excel formulas
- units
- function names
- zone tokens
- dimension casing
- custom quantities
- item codes
- headings
- workbook structure
- source rows
- level names
- aliases

Any normalization must be explicit, testable, and reversible.

---

## 11. Test and Retest Rule

After each batch, run the required tests for that batch.

After the final batch, run full regression:

- compile check
- pytest
- all JSON packs
- safety aggregate
- duplicate route scan
- duplicate top-level class/function scan
- execution flag scan
- protected file/hash check when relevant

A build is not valid until tests prove it.

---

## 12. Report Requirements After FIRE

After every approved build, report:

- version name
- base version used
- files changed
- functions changed
- what was fixed
- what was not touched
- tests performed
- test results
- remaining risks
- rollback notes
- next test instructions

Do not claim something is fixed unless tests prove it.

---

## 13. Confidence Gate

Before FIRE, provide:

- confidence percentage
- exact files/functions affected
- evidence supporting the patch
- what remains uncertain
- regression tests
- protected stable logic that will not be touched

Do not recommend FIRE if confidence is below 95%, unless the patch is very small and the remaining risk is clearly explained.

---

## 14. Handoff Rule

Every major build should include a handoff file containing:

- current version
- base version
- scope
- files changed
- known issues
- protected files
- test results
- next recommended patch
- what not to do next
- rollback notes

---

## 15. Future Handoff Continuity Rule

Every future Jarvis handoff must be written for zero-context-loss continuation.

The handoff must include enough information for a new chat to continue safely without guessing.

Each handoff must include:

- current version
- base version used
- project purpose
- active development phase
- latest completed build
- exact scope of latest build
- files changed
- functions changed
- tests performed
- test results
- known issues
- unresolved risks
- protected files and logic
- what must not be touched next
- next recommended dry run
- next recommended FIRE scope
- rollback point
- source files required for the next chat
- missing/expired files, if any
- current safety locks
- current execution status
- router/state ownership notes
- active Builder/Formatter/QA/O&A roadmap status

A future handoff must not assume the next chat remembers prior context.

The next chat must start by performing a source inventory and continuity check before planning or patching.

The next chat must separate:

- confirmed evidence
- likely conclusions
- hypotheses

The next chat must not patch until the source inventory and continuity check are complete.

---

## 16. Deep Continuity Research Rule

At the start of every new Jarvis development chat, and before any major dry run, the assistant must perform a deep continuity review of the available project source.

This review must include:

- inventory of readable files
- inventory of missing or expired files
- current source ZIP/package check
- current version check
- base version check
- relevant handoff files
- latest change report
- latest test report
- latest pack results
- current docs
- current router/state/policy ownership
- protected sensitive files
- current safety flags
- known roadmap position

The assistant must not claim it has read unavailable or expired files.

When files are missing, the assistant must state what is missing and whether the missing file is required before continuing.

The goal is to prevent Jarvis development context loss across chats.

---

## 17. Dry Run Must Provide Best FIRE Prompt

Every Jarvis dry run must end with a safe, copy-ready FIRE prompt for the user.

The FIRE prompt must be scoped, batch-aware, and include all protection rules.

The FIRE prompt must include:

- target version
- base version
- exact scope
- batch-by-batch execution rule
- allowed files
- disallowed files
- safety locks that must remain false
- protected logic not to touch
- required tests
- stop condition if any batch fails
- final report requirements

The FIRE prompt must not include broad or vague permissions.

The FIRE prompt must not allow unrelated fixes.

The FIRE prompt must not enable workbook reading, Builder engine execution, legacy Builder calling, Excel output, Formatter, QA Checker, O&A, or UI changes unless that is explicitly the approved scope.

---

## 18. Chat Context Archive Rule

Every major Jarvis handoff must include a Markdown chat-context archive so the next chat can continue without losing development context.

The archive should be saved as a Markdown file, for example:

- `CHAT_CONTEXT_ARCHIVE_v5_alpha_28.md`
- or included as a section inside `NEXT_CHAT_HANDOFF_v5_alpha_28.md`

The archive must include the useful user-visible context from the current chat, including:

- user instructions
- agreed rules
- active task
- current version
- base version
- current diagnosis
- dry-run decisions
- planned patch batches
- rejected unsafe actions
- protected files and logic
- known risks
- test expectations
- next recommended action
- best FIRE prompt from the latest dry run

The archive must preserve safe reasoning summaries, including:

- why a patch is needed
- why a patch is deferred
- why a file is sensitive
- why a route owner must stay isolated
- why a batch must stop on failure
- what evidence supports confidence
- what remains uncertain

The archive must not include unavailable private hidden reasoning or anything unsafe/restricted.

Instead of hidden reasoning, include a clear user-visible reasoning summary:

- confirmed evidence
- likely conclusions
- hypotheses
- decisions made
- risks and mitigations

The archive must not claim that expired or unread files were inspected.

The archive must clearly state:

- files that were read
- files that were missing or expired
- source ZIP used
- tests actually run
- tests only recommended but not run

The goal is zero practical context loss without exposing private or restricted content.


## Package Cleanup and Version Tag Hygiene Rule

Before every final ZIP/package:

- remove temporary work folders
- remove `__pycache__`, `.pyc`, and `.pytest_cache`
- remove generated test reports unless intentionally retained
- archive previous-version root release artifacts under `docs/version_history/<version>/`
- keep only current-version release artifacts in the final ZIP root
- ensure current version tags, reports, handoff, backend status, start scripts, and pack results match the target version
- run ZIP root inventory check before the final report
- do not ship stale previous-version reports, handoffs, status files, test results, pack results, or BAT scripts in the package root

## Dormant Code Preservation Rule

Dormant code is not automatically useless code. If a file, function, schema, or helper is reserved for a future tool, route, schema, policy, output contract, or debug workflow, it must be documented before deletion is considered.

Do not delete dormant code unless all of these are true:

1. It has no documented future owner.
2. It has no current or planned route/tool family.
3. It is not referenced by roadmap, handoff, docs, tests, or registry.
4. It is not part of a safety boundary, schema boundary, debug boundary, or future output contract.
5. A dedicated dry run confirms deletion is safe.
6. The user explicitly approves deletion.

Every dormant-code audit must classify findings as Reserved, Watchlist, Candidate for deletion, or Deprecated.
