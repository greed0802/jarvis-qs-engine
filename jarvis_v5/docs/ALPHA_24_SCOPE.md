# Jarvis v5.0.0-alpha.24 — Route Ownership Hardening + Registry Advisory Route Contract, no execution

## Scope

Alpha.24 repairs route ownership gaps found after alpha.23 registry metadata was added.

## Added

1. `active_task_action_language_gate.py` for natural active Review / Preview / Export / Download phrases.
2. Setup text normalization for unit correction and reversed zone wording, still routed through `slot_reducer`.
3. BOQ advisory disqualifiers for report/checklist/future-tool language.
4. `registry_advisory_metadata_only` route contract.
5. `measure schedule` soft Builder alias.
6. QA runner known-route cleanup.
7. Confirmed stale alpha22 root package artifacts archived into version history.

## Protected

No Builder engine, legacy Builder execution, workbook reading/parsing, formula generation, Excel output, Formatter, QA Checker, O&A, snapshot, adapter, contract, preflight, execution, registry execution flags, or UI redesign were touched.
