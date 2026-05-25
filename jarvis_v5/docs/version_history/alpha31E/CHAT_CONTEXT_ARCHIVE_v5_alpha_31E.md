# Chat Context Archive — v5.0.0-alpha.31E

This build continued the alpha.31 weakness-pack cleanup sequence after alpha.31D.

## Active instruction

FIRE v5.0.0-alpha.31E only: Parser Signal Helper Consolidation + Formworks Unit Conflict Guard, no workbook read.

## Confirmed evidence

- Base alpha.31D passed standard regression.
- Weakness packs 041–045 had one remaining failing phrase: `Use XGETCUSTOM Formworks unit t`.
- Root cause was missing compatibility rule for `XGETCUSTOM + Formworks`.
- Parser signal helper names were duplicated between `trade_parser.py` and `conflict_guard.py`.

## Decision

Add one parser signal helper owner and a narrow Formworks unit compatibility guard.

## Safety decisions

- No workbook read.
- No Builder engine.
- No legacy Builder.
- No Excel output.
- No broad unit ontology.
- No router behavior changes.

## Final result

Alpha.31E passed standard tests, standard JSON packs, targeted weakness subset 041–045, and active route stability subset.
