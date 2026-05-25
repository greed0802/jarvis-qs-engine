# v5.0.0-alpha.31E Scope

Parser Signal Helper Consolidation + Formworks Unit Conflict Guard, no workbook read.

## Included

- Add one shared parser signal helper owner: `jarvis_v5/parsers/setup_signal_helpers.py`.
- Update `trade_parser.py` and `conflict_guard.py` to use the shared signal helper owner.
- Add narrow compatibility rule: `XGETCUSTOM + Formworks` allows unit `m2`.
- Block `Use XGETCUSTOM Formworks unit t` with function/unit clarification instead of mutating the plan.
- Add smoke tests, JSON pack, targeted weakness subset report, package hygiene report, and handoff docs.

## Excluded

- No workbook read/open/parse.
- No Builder engine call.
- No Excel output.
- No legacy Builder call.
- No router ownership changes.
- No UI, Formatter, QA Checker, O&A, or Output Center changes.
- No broad unit ontology.
