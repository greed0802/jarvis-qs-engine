from __future__ import annotations

from typing import Any


def default_builder_shell_plan(raw_command: str = "") -> dict[str, Any]:
    """Create the alpha.3 Builder shell plan.

    This is state only. It does not read workbooks, generate formulas, or call
    Builder/Formatter/QA engines.
    """
    return {
        "source": "v5_alpha3_builder_shell",
        "raw_command": raw_command,
        "trade_profile": None,
        "costx_function": None,
        "custom_quantity": None,
        "unit": None,
        "dynamic_zones": [],
        "heading_assignments": {},
        "levels": [],
        "aliases": {},
        "item_code_settings": {},
        "trade_registry": None,
        "warnings": [],
        "confidence": 0.0,
    }


def ensure_builder_shell_plan(plan: dict[str, Any] | None) -> dict[str, Any]:
    base = default_builder_shell_plan((plan or {}).get("raw_command", ""))
    if plan:
        base.update(plan)
    base.setdefault("dynamic_zones", [])
    base.setdefault("heading_assignments", {})
    base.setdefault("levels", [])
    base.setdefault("aliases", {})
    base.setdefault("item_code_settings", {})
    base.setdefault("warnings", [])
    base.setdefault("trade_registry", None)
    return base


def plan_summary(plan: dict[str, Any]) -> dict[str, Any]:
    plan = ensure_builder_shell_plan(plan)
    return {
        "trade_profile": plan.get("trade_profile"),
        "costx_function": plan.get("costx_function"),
        "custom_quantity": plan.get("custom_quantity"),
        "unit": plan.get("unit"),
        "zones": plan.get("dynamic_zones") or [],
        "heading_assignments": plan.get("heading_assignments") or {},
        "levels": plan.get("levels") or [],
        "aliases": plan.get("aliases") or {},
        "trade_registry": plan.get("trade_registry"),
        "warnings": plan.get("warnings") or [],
        "confidence": plan.get("confidence") or 0.0,
    }


def summarize_builder_plan(plan: dict[str, Any]) -> list[str]:
    plan = ensure_builder_shell_plan(plan)
    lines: list[str] = [
        "",
        "Setup",
        f"Trade/Profile: {plan.get('trade_profile') or 'not set'}",
        f"Function: {plan.get('costx_function') or 'not set'}",
        f"Custom quantity: {plan.get('custom_quantity') or 'not set'}",
        f"Unit: {plan.get('unit') or 'not set'}",
        f"Trade registry: {(plan.get('trade_registry') or {}).get('registry_key') or 'not matched'}",
        "",
        "Zones",
    ]
    zones = plan.get("dynamic_zones") or []
    if zones:
        for zone in zones:
            values = ", ".join(zone.get("values") or []) or "(no values)"
            head = zone.get("head_assignment") or plan.get("heading_assignments", {}).get(str(zone.get("zone_id")))
            suffix = f" → {head}" if head else ""
            lines.append(f"Zone {zone.get('zone_id')}: {values}{suffix}")
    else:
        lines.append("No zones set")
    lines.extend(["", "Levels"])
    if plan.get("levels"):
        lines.append(", ".join(plan.get("levels") or []))
    else:
        lines.append("No levels set")
    lines.extend(["", "Notes", "Preview/export engines are not connected in v5 alpha.4."])
    return lines
