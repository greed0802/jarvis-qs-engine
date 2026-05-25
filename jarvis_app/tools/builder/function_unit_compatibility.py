from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


COUNT_UNITS = {"no", "nr", "count", "item", "each", "pcs"}
AREA_UNITS = {"m2"}
VOLUME_UNITS = {"m3"}
LENGTH_UNITS = {"lm", "m"}
WEIGHT_UNITS = {"t", "kg"}

FUNCTION_ALLOWED_UNITS: dict[str, set[str]] = {
    "XGETCOUNT": COUNT_UNITS,
    "XGETWALLAREA": AREA_UNITS,
    "XGETAREA": AREA_UNITS,
    "XGETVOLUME": VOLUME_UNITS,
    "XGETLENGTH": LENGTH_UNITS,
}

UNIT_ALIASES = {
    "nos": "no",
    "number": "no",
    "numbers": "no",
    "nr.": "nr",
    "each": "each",
    "ea": "each",
    "pc": "pcs",
    "pcs": "pcs",
    "piece": "pcs",
    "pieces": "pcs",
    "sqm": "m2",
    "sq.m": "m2",
    "sq. m": "m2",
    "sq m": "m2",
    "sq metre": "m2",
    "sq metres": "m2",
    "sq meter": "m2",
    "sq meters": "m2",
    "square metre": "m2",
    "square metres": "m2",
    "square meter": "m2",
    "square meters": "m2",
    "m²": "m2",
    "cu.m": "m3",
    "cu m": "m3",
    "m³": "m3",
    "linear meter": "lm",
    "linear metre": "lm",
    "lin m": "lm",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_unit(unit: str | None) -> str | None:
    if unit is None:
        return None
    value = str(unit).strip().lower()
    if not value:
        return None
    return UNIT_ALIASES.get(value, value)


def normalize_function(costx_function: str | None) -> str | None:
    if costx_function is None:
        return None
    value = str(costx_function).strip().upper()
    return value or None


def allowed_units_for_function(costx_function: str | None, *, custom_quantity: str | None = None) -> set[str] | None:
    function = normalize_function(costx_function)
    if not function:
        return None
    if function == "XGETCUSTOM":
        # Keep XGETCUSTOM conservative. Only validate known custom quantities here;
        # do not build a broad unit ontology before the real engine is connected.
        qty = str(custom_quantity or "").strip().lower()
        if qty in {"reinforcement weight", "bar reinforcement weight"}:
            return {"t"}
        if qty == "steel surface area":
            return {"m2"}
        if qty in {"formwork", "formworks"}:
            return {"m2"}
        return None
    return FUNCTION_ALLOWED_UNITS.get(function)


def validate_function_unit_compatibility(
    *,
    costx_function: str | None,
    unit: str | None,
    trade_profile: str | None = None,
    custom_quantity: str | None = None,
) -> dict[str, Any]:
    function = normalize_function(costx_function)
    normalized_unit = normalize_unit(unit)
    if not function or not normalized_unit:
        return {"valid": True, "checked": False, "reason": "missing_function_or_unit"}

    allowed = allowed_units_for_function(function, custom_quantity=custom_quantity)
    if allowed is None:
        return {"valid": True, "checked": False, "reason": "no_rule_for_function"}

    valid = normalized_unit in allowed
    return {
        "valid": valid,
        "checked": True,
        "conflict_type": None if valid else "function_unit_conflict",
        "function": function,
        "unit": normalized_unit,
        "trade_profile": trade_profile,
        "custom_quantity": custom_quantity,
        "allowed_units": sorted(allowed),
        "message": None if valid else _message(function, normalized_unit, sorted(allowed)),
    }


def _message(function: str, unit: str, allowed_units: list[str]) -> str:
    allowed_text = ", ".join(allowed_units)
    return f"{function} normally uses unit {allowed_text}. You selected {unit}. Choose a compatible unit or change the CostX function."


def compatibility_conflict_payload(compat: dict[str, Any]) -> dict[str, Any]:
    function = compat.get("function") or "CostX function"
    unit = compat.get("unit") or "unit"
    allowed = compat.get("allowed_units") or []
    prompt = compat.get("message") or "The CostX function and unit are not compatible. Which setup should I use?"
    options = [f"Use {function} with unit {allowed[0]}"] if allowed else []
    options.extend(["Change the CostX function", "Cancel"])
    return {
        "conflict_type": "function_unit_conflict",
        "conflicting_slots": ["costx_function", "unit"],
        "options": options,
        "message": prompt,
        "clarification": {
            "clarification_id": f"clar_{uuid.uuid4().hex}",
            "type": "function_unit_conflict",
            "prompt": prompt,
            "options": options,
            "expected_answer_classes": ["choice", "cancel"],
            "resolver_name": "resolve_parser_conflict_guard",
            "context": {
                "function": function,
                "unit": unit,
                "allowed_units": allowed,
                "trade_profile": compat.get("trade_profile"),
                "custom_quantity": compat.get("custom_quantity"),
            },
            "repeats": 0,
            "max_repeats": 2,
            "status": "open",
            "created_at": _now(),
            "updated_at": _now(),
        },
    }
