from __future__ import annotations


def apply_trade_function_unit_changes(plan: dict, changes: dict) -> None:
    for key in ["trade_profile", "costx_function", "custom_quantity", "unit", "trade_registry"]:
        if key in changes:
            plan[key] = changes[key]
