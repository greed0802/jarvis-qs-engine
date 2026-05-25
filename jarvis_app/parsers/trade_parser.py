from __future__ import annotations

from typing import Any

from jarvis_v5.router.action_aliases import normalize_text
from jarvis_v5.registry.trade_profile_registry import find_trade_registry_match, clean_trade_registry_payload
from jarvis_v5.parsers.setup_signal_helpers import (
    detect_custom_quantity_signals,
    detect_function_signals,
    detect_trade_signals,
    detect_unit_signals,
    has_explicit_reinforcement_weight_t_setup,
    is_direct_concrete_reo_setup,
)


def parse_trade_function_unit(text: str) -> dict[str, Any] | None:
    normalized = normalize_text(text)
    if not normalized:
        return None

    registry_match = find_trade_registry_match(text)
    trades = detect_trade_signals(normalized, include_registry=True)
    functions = detect_function_signals(normalized)
    quantities = detect_custom_quantity_signals(text)
    units = detect_unit_signals(text, prefer_explicit_units=True)

    changes: dict[str, Any] = {}
    message_parts: list[str] = []
    trade_registry = clean_trade_registry_payload(registry_match)

    if registry_match and registry_match.get("requires_clarification") and not has_explicit_reinforcement_weight_t_setup(text) and not is_direct_concrete_reo_setup(text):
        # Ambiguous/high-risk registry matches are handled by the conflict guard.
        return None

    if trades:
        changes["trade_profile"] = trades[0]
        message_parts.append(f"trade/profile to {trades[0]}")
        if trade_registry:
            changes["trade_registry"] = trade_registry

    if functions:
        changes["costx_function"] = functions[0]
        message_parts.append(f"function to {functions[0]}")
    if quantities:
        changes["custom_quantity"] = quantities[0]
        if "costx_function" not in changes:
            changes["costx_function"] = "XGETCUSTOM"
        message_parts.append(f"custom quantity to {quantities[0]}")
    if units:
        changes["unit"] = units[0]
        message_parts.append(f"unit to {units[0]}")

    if not changes:
        return None
    return {
        "changes": changes,
        "message_parts": message_parts,
        "confidence": 0.9 if not trade_registry else 0.92,
        "trade_registry": trade_registry,
    }
