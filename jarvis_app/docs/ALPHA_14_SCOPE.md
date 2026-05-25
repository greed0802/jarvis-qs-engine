# v5.0.0-alpha.14 — Trade Profile Registry + Alias Normalization, no engine

## Scope

Alpha.14 adds a controlled QS trade/profile registry for common trade aliases.

It normalizes low-risk known trades to a canonical `trade_profile` only, and asks clarification for ambiguous/high-risk trades before mutating the Builder shell plan.

## Added

- `jarvis_v5/registry/trade_profile_registry.json`
- `jarvis_v5/registry/trade_profile_registry.py`
- Low-risk trade alias normalization:
  - Carpet
  - Tiling
  - Plaster / Render
  - Insulation
  - Waterproofing
  - Roofing
- Clarification-first handling for ambiguous/high-risk trades:
  - Painting
  - Joinery
  - Fencing
  - Scaffold
  - Demolition
  - Earthworks
  - Landscaping
  - Reinforcement
  - Metalwork
  - Brickwork
- `trade_registry` metadata carried through reducer, plan, snapshot, adapter, contract, and boundary audit paths where relevant.

## Safety boundary

Alpha.14 does not connect any real tool engine.

Required locks:

- `workbook_read=false`
- `engine_called=false`
- `excel_created=false`
- `contract_only=true`
- `legacy_builder_called=false`

## Protected systems

Not touched:

- Builder engine
- workbook reading/parsing
- formula generation
- Excel output
- Formatter
- QA
- O&A
- UI redesign
- current Jarvis replacement
