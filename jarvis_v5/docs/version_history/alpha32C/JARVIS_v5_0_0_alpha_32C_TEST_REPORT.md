# Test Report — v5.0.0-alpha.32C

## Summary

| Check | Result |
|---|---:|
| Python compile | PASS |
| Pytest | PASS — 268 passed |
| Built-in JSON packs | PASS — 37 / 37 packs |
| Built-in JSON tests | PASS — 171 / 171 tests |
| Duplicate FastAPI routes | PASS — 0 |
| Same-file duplicate top-level definitions | PASS — 0 |
| Cross-file duplicate classification | PASS — 29 classified, 0 runtime-risk |
| Protected Builder boundary hash check | PASS — 9 / 9 unchanged |
| Package root stale previous-version artifacts | PASS — 0 |

## Safety aggregate

- workbook_read_any_true=false
- engine_called_any_true=false
- excel_created_any_true=false
- legacy_builder_called_any_true=false

## 8,000 weakness replay

Not rerun for alpha.32C. alpha.32B already completed the full 8,000 replay with effective non-version failures = 0, and alpha.32C is docs/allowlist only.
