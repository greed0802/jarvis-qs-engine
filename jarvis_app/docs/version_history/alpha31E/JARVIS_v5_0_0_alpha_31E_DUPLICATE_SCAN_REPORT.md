# Duplicate Scan Report — v5.0.0-alpha.31E

## Summary

- Duplicate FastAPI routes: 0
- Same-file duplicate top-level definitions: 0
- Cross-file duplicate helper/function names: 29 documented only

## Parser signal duplicate result

The parser signal helper consolidation moved shared signal ownership into:

- `jarvis_v5/parsers/setup_signal_helpers.py`

This reduced cross-file helper duplicates from 35 in alpha.31D to 29 in alpha.31E.

## Deferred duplicates

Remaining cross-file duplicates are not duplicate routes and were not fixed in this build unless they belonged to parser signal helper ownership. They remain watchlist/documented only.
