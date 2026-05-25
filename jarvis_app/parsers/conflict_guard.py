from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any

from jarvis_v5.router.action_aliases import normalize_text
from jarvis_v5.registry.trade_profile_registry import find_trade_registry_match, trade_registry_clarification, clean_trade_registry_payload, load_trade_profile_registry
from jarvis_v5.tools.builder.function_unit_compatibility import COUNT_UNITS


from jarvis_v5.parsers.setup_signal_helpers import (
    detect_custom_quantity_signals,
    detect_function_signals,
    detect_trade_signals,
    detect_unit_signals,
    has_explicit_reinforcement_weight_t_setup,
    is_direct_concrete_reo_setup,
    unique_signal_values,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _word_pattern(alias: str) -> str:
    parts = [re.escape(part) for part in normalize_text(alias).split()]
    return r"\b" + r"\s+".join(parts) + r"\b"


def _detect_registry_trade_choices(text: str) -> list[dict[str, Any]]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    registry = load_trade_profile_registry()
    matches: list[dict[str, Any]] = []
    seen: set[str] = set()
    for key, profile in (registry.get("profiles") or {}).items():
        aliases = profile.get("aliases") or [key]
        for alias in aliases:
            if re.search(_word_pattern(str(alias)), normalized, flags=re.I):
                if key in seen:
                    continue
                seen.add(key)
                matches.append({
                    "registry_key": key,
                    "input": str(alias),
                    "canonical_trade": profile.get("canonical_trade"),
                    "risk": profile.get("risk"),
                    "normalization_mode": profile.get("normalization_mode"),
                })
                break
    return matches


def _normalization_status(plan: dict[str, Any] | None, warnings: list[str] | None = None, conflicts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "status": "needs_clarification" if conflicts else "clean",
        "warnings": warnings or [],
    }


def _clarification(conflict_type: str, prompt: str, options: list[str], context: dict[str, Any]) -> dict[str, Any]:
    return {
        "clarification_id": f"clar_{uuid.uuid4().hex}",
        "type": conflict_type,
        "prompt": prompt,
        "options": options,
        "expected_answer_classes": ["choice", "cancel"],
        "resolver_name": "resolve_parser_conflict_guard",
        "context": context,
        "repeats": 0,
        "max_repeats": 2,
        "status": "open",
        "created_at": _now(),
        "updated_at": _now(),
    }



def detect_setup_conflict(plan: dict[str, Any] | None, text: str) -> dict[str, Any] | None:
    """Detect clear conflicts/ambiguity before mutating a Builder shell plan.

    Alpha.9 intentionally blocks only high-confidence conflicts. It does not
    attempt to validate formulas, inspect workbooks, or call any engine.
    """
    plan = plan or {}
    normalized = normalize_text(text)
    if not normalized:
        return None


    registry_choices = _detect_registry_trade_choices(text)
    if len(registry_choices) > 1 and re.search(r"\b(?:or|either)\b", normalized):
        prompt = "I found more than one possible trade/profile. Choose one before I update the Builder setup."
        options = [f"Use {choice.get('input') or choice.get('canonical_trade')}" for choice in registry_choices] + ["Cancel"]
        return {
            "conflict_type": "trade_choice_ambiguous",
            "conflicting_slots": ["trade_profile"],
            "options": options,
            "message": f"{prompt} Options: {', '.join(options)}",
            "clarification": _clarification("trade_choice_ambiguous", prompt, options, {"trade_choices": registry_choices}),
        }

    registry_match = find_trade_registry_match(text)
    if registry_match and registry_match.get("requires_clarification") and not has_explicit_reinforcement_weight_t_setup(text) and not is_direct_concrete_reo_setup(text):
        clarification = trade_registry_clarification(registry_match)
        return {
            "conflict_type": "trade_profile_requires_clarification",
            "conflicting_slots": ["trade_profile"],
            "options": clarification.get("options") or [],
            "message": clarification.get("prompt") or "This trade profile needs clarification before I update the Builder setup.",
            "clarification": clarification,
            "trade_registry": clean_trade_registry_payload(registry_match),
        }

    trades = detect_trade_signals(normalized)
    if len(trades) > 1:
        prompt = "I found more than one trade/profile. Choose one before I update the Builder setup."
        options = [f"Use {trade}" for trade in trades] + ["Cancel"]
        return {
            "conflict_type": "trade_conflict",
            "conflicting_slots": ["trade_profile"],
            "options": options,
            "message": f"{prompt} Options: {', '.join(options)}",
            "clarification": _clarification("trade_conflict", prompt, options, {"trades": trades}),
        }

    functions = detect_function_signals(normalized, include_weight_quantities=False)
    if len(functions) > 1:
        prompt = "I found more than one CostX function. Choose one before I update the Builder setup."
        options = [f"Use {function}" for function in functions] + ["Cancel"]
        return {
            "conflict_type": "function_conflict",
            "conflicting_slots": ["costx_function"],
            "options": options,
            "message": f"{prompt} Options: {', '.join(options)}",
            "clarification": _clarification("function_conflict", prompt, options, {"functions": functions}),
        }

    units = detect_unit_signals(normalized, include_weight_quantities=False)
    custom_quantities = detect_custom_quantity_signals(normalized, include_weight_quantities=False)

    # Clear function/unit mismatch guards.
    if "XGETCOUNT" in functions and units and any(unit not in COUNT_UNITS for unit in units):
        prompt = 'Count usually uses a count unit such as no, nr, count, item, each, or pcs. Which setup should I use?'
        options = ["Use XGETCOUNT with unit no", "Use XGETCOUNT with unit nr", "Keep the stated unit and choose another function later", "Cancel"]
        return {
            "conflict_type": "function_unit_conflict",
            "conflicting_slots": ["costx_function", "unit"],
            "options": options,
            "message": prompt,
            "clarification": _clarification("function_unit_conflict", prompt, options, {"function": "XGETCOUNT", "units": units}),
        }

    if "Steel Surface Area" in custom_quantities and units and any(unit != "m2" for unit in units):
        prompt = 'Steel Surface Area usually uses unit "m2", but you said another unit. Which setup should I use?'
        options = ["Use Steel Surface Area with unit m2", "Keep the stated unit and choose another quantity later", "Cancel"]
        return {
            "conflict_type": "custom_quantity_unit_conflict",
            "conflicting_slots": ["custom_quantity", "unit"],
            "options": options,
            "message": prompt,
            "clarification": _clarification("custom_quantity_unit_conflict", prompt, options, {"custom_quantity": "Steel Surface Area", "units": units}),
        }

    # Heading assignment ambiguity: "Use Head 2" without a zone is safe only
    # when there is exactly one dynamic zone already in the plan.
    if re.search(r"\b(?:use|set|change)?\s*head\s*([1-4])\b", normalized) and not re.search(r"\bzone\s*\d+\b", normalized):
        zone_ids = [int(z.get("zone_id")) for z in (plan.get("dynamic_zones") or []) if z.get("zone_id") is not None]
        if len(zone_ids) > 1:
            head = re.search(r"\bhead\s*([1-4])\b", normalized).group(1)
            prompt = f"Which zone should use Head{head}?"
            options = [f"Use Head{head} for Zone {zone_id}" for zone_id in zone_ids] + ["Cancel"]
            return {
                "conflict_type": "heading_ambiguity",
                "conflicting_slots": ["heading_assignments"],
                "options": options,
                "message": prompt,
                "clarification": _clarification("heading_ambiguity", prompt, options, {"head": f"Head{head}", "zone_ids": zone_ids}),
            }

    # Alpha.24.1: heading assignment to a not-yet-defined zone is metadata-only and safe.
    # Future engine readiness still requires dynamic zone values before any engine connection.

    # Basement ranges can be project-specific. Descending ranges like B3 to B1
    # are explicit/conventional and can be stored as B3, B2, B1. Longer
    # ascending basement ranges such as B2 to B5 remain ambiguous and should
    # ask before storing.
    basement = re.search(r"\b(?:levels?\s+)?b\s*(\d+)\s+to\s+b\s*(\d+)\b", normalized, flags=re.I)
    if basement:
        a = int(basement.group(1))
        b = int(basement.group(2))
        if b > a and abs(a - b) > 1:
            prompt = f"Confirm basement order for B{a} to B{b}."
            down = [f"B{i}" for i in range(b, a - 1, -1)]
            up = [f"B{i}" for i in range(a, b + 1)]
            options = [", ".join(down), ", ".join(up), "Cancel"]
            return {
                "conflict_type": "ambiguous_basement_range",
                "conflicting_slots": ["levels"],
                "options": options,
                "message": prompt,
                "clarification": _clarification("ambiguous_basement_range", prompt, options, {"start": f"B{a}", "end": f"B{b}", "options": options[:2]}),
            }

    return None


def plan_normalization_report(plan: dict[str, Any] | None, *, conflicts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    warnings: list[str] = []
    plan = plan or {}
    for zone in plan.get("dynamic_zones") or []:
        for value in zone.get("values") or []:
            text = str(value).strip()
            if not text:
                warnings.append("Blank zone value")
            if re.search(r"\b(?:use\s+head|levels?|preview|export)\b", text, flags=re.I):
                warnings.append(f"Suspicious zone value: {text}")
    report = _normalization_status(plan, warnings=warnings, conflicts=conflicts)
    if plan.get("trade_registry"):
        report["trade_registry"] = plan.get("trade_registry")
    return report
