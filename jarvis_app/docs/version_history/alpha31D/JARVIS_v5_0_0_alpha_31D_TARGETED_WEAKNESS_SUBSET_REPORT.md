# Targeted Weakness Subset Report — v5.0.0-alpha.31D

## Targeted subset

- 035–039 pending_clarification_blocks_actions
- 040 pending_clarification_review_allowed

## Result

- 035–039: PASS — 250 / 250
- 040: PASS — 50 / 50
- Combined: PASS — 300 / 300

## Confirmed behavior

- `Run builder now` is now blocked while pending clarification is open.
- Review remains allowed while pending clarification is open.
- Valid clarification answers still resolve.
- Parser/function-unit conflict failures remain deferred and out of scope.
