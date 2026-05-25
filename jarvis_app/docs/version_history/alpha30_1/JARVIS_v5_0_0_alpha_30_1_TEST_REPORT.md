# Jarvis v5.0.0-alpha.30.1 Test Report

## Test results

| Check | Result |
|---|---|
| `python -m compileall -q jarvis_v5` | PASS |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` | PASS — 234 passed |
| Standard JSON packs | PASS — 30 / 30 packs |
| JSON pack tests | PASS — 123 / 123 tests |
| Duplicate FastAPI route scan | PASS — 0 duplicates |
| Same-file top-level definition scan | PASS — 0 duplicates |
| Cross-file helper/function duplicate scan | INFO — 33 documented |
| Protected Builder boundary hash check | PASS — 10 / 10 unchanged |
| ZIP root stale previous-version artifact check | PASS |

## Safety aggregate

```text
workbook_read_any_true=false
engine_called_any_true=false
excel_created_any_true=false
legacy_builder_called_any_true=false
```

## 8,000-test weakness evidence preserved

The external weakness pack result remains: 5985 passed, 2015 failed, safety aggregate held. Alpha.30.1 does not attempt to fix those failures; it documents and sequences them.
