from __future__ import annotations

from typing import Any

from jarvis_v5.tools.builder.function_unit_compatibility import validate_function_unit_compatibility


def _label(slot: str) -> str:
    return {
        "workbook_ref": "Workbook",
        "trade_profile": "Trade/Profile",
        "costx_function": "CostX function",
        "custom_quantity": "Custom quantity",
        "unit": "Unit",
        "dynamic_zones": "Dynamic zones",
        "heading_assignments": "Heading assignments",
        "levels": "Levels",
        "pending_clarification": "Pending clarification",
        "function_unit_compatibility": "Function/unit compatibility",
        "snapshot_current": "Current snapshot",
        "adapter_current": "Current adapter dry run",
    }.get(slot, slot.replace("_", " ").title())


def _has_custom_quantity_requirement(costx_function: str | None) -> bool:
    return str(costx_function or "").upper() == "XGETCUSTOM"


def _is_preserve_source_count_mode(plan_or_snapshot: dict[str, Any]) -> bool:
    function = str(plan_or_snapshot.get("costx_function") or "").upper()
    unit = str(plan_or_snapshot.get("unit") or "").lower()
    zone_mode = str(plan_or_snapshot.get("zone_mode") or "rebuild").lower()
    return zone_mode == "preserve_source" and function == "XGETCOUNT" and unit == "no"


def setup_completeness_from_parts(
    *,
    workbook_ref: dict[str, Any] | None = None,
    trade_profile: str | None = None,
    costx_function: str | None = None,
    custom_quantity: str | None = None,
    unit: str | None = None,
    zone_mode: str | None = "rebuild",
    dynamic_zones: list[dict[str, Any]] | None = None,
    heading_assignments: dict[str, Any] | None = None,
    levels: list[str] | None = None,
    pending_clarification: bool = False,
    snapshot_status: str | None = None,
    adapter_freshness: str | None = None,
) -> dict[str, Any]:
    dynamic_zones = dynamic_zones or []
    heading_assignments = heading_assignments or {}
    levels = levels or []
    zone_mode = zone_mode or "rebuild"
    missing: list[str] = []
    warnings: list[str] = []

    if not workbook_ref:
        missing.append("workbook_ref")
    if not trade_profile:
        missing.append("trade_profile")
    if not costx_function:
        missing.append("costx_function")
    if _has_custom_quantity_requirement(costx_function) and not custom_quantity:
        missing.append("custom_quantity")
    if not unit:
        missing.append("unit")
    compat = validate_function_unit_compatibility(
        costx_function=costx_function,
        unit=unit,
        trade_profile=trade_profile,
        custom_quantity=custom_quantity,
    )
    if compat.get("checked") and not compat.get("valid"):
        missing.append("function_unit_compatibility")
        warnings.append(compat.get("message") or "CostX function and unit are not compatible.")
    if str(zone_mode).lower() == "rebuild":
        if not dynamic_zones:
            missing.append("dynamic_zones")
        if not heading_assignments:
            missing.append("heading_assignments")
    preserve_source_count = _is_preserve_source_count_mode({
        "costx_function": costx_function,
        "unit": unit,
        "zone_mode": zone_mode,
    })
    if not levels and not preserve_source_count:
        missing.append("levels")
    if pending_clarification:
        missing.append("pending_clarification")
    if snapshot_status and snapshot_status != "current":
        missing.append("snapshot_current")
    if adapter_freshness and adapter_freshness != "current":
        missing.append("adapter_current")

    if workbook_ref and missing:
        warnings.append("Workbook is attached but setup is not complete for future Builder engine.")
    elif not workbook_ref:
        warnings.append("Workbook is not attached yet.")

    next_actions = [f"Set {_label(slot).lower()}" for slot in missing]
    ready_for_dry_run = True
    ready_for_future_engine = not missing
    status = "ready_for_future_engine" if ready_for_future_engine else "incomplete"

    return {
        "status": status,
        "ready_for_dry_run": ready_for_dry_run,
        "ready_for_future_engine": ready_for_future_engine,
        "missing_required": missing,
        "missing_labels": [_label(slot) for slot in missing],
        "warnings": warnings,
        "next_actions": next_actions,
    }


def setup_completeness_from_plan(
    *,
    plan: dict[str, Any] | None,
    workbook_ref: dict[str, Any] | None = None,
    pending_clarification: bool = False,
    snapshot_status: str | None = None,
    adapter_freshness: str | None = None,
) -> dict[str, Any]:
    plan = plan or {}
    return setup_completeness_from_parts(
        workbook_ref=workbook_ref,
        trade_profile=plan.get("trade_profile"),
        costx_function=plan.get("costx_function"),
        custom_quantity=plan.get("custom_quantity"),
        unit=plan.get("unit"),
        zone_mode=plan.get("zone_mode") or "rebuild",
        dynamic_zones=plan.get("dynamic_zones") or [],
        heading_assignments=plan.get("heading_assignments") or {},
        levels=plan.get("levels") or [],
        pending_clarification=pending_clarification,
        snapshot_status=snapshot_status,
        adapter_freshness=adapter_freshness,
    )


def setup_completeness_from_snapshot(snapshot: Any, *, pending_clarification: bool = False, adapter_freshness: str | None = None) -> dict[str, Any]:
    if hasattr(snapshot, "model_dump"):
        data = snapshot.model_dump(mode="json")
    else:
        data = snapshot or {}
    return setup_completeness_from_parts(
        workbook_ref=data.get("workbook_ref"),
        trade_profile=data.get("trade_profile"),
        costx_function=data.get("costx_function"),
        custom_quantity=data.get("custom_quantity"),
        unit=data.get("unit"),
        zone_mode=data.get("zone_mode") or "rebuild",
        dynamic_zones=data.get("dynamic_zones") or [],
        heading_assignments=data.get("heading_assignments") or {},
        levels=data.get("levels") or [],
        pending_clarification=pending_clarification,
        snapshot_status=data.get("status"),
        adapter_freshness=adapter_freshness,
    )


def format_setup_completeness_lines(setup: dict[str, Any] | None) -> list[str]:
    if not setup:
        return []
    lines = [
        "",
        "Setup completeness",
        f"Status: {setup.get('status')}",
        f"Dry run: {'ready' if setup.get('ready_for_dry_run') else 'not ready'}",
        f"Future engine: {'ready' if setup.get('ready_for_future_engine') else 'not ready'}",
    ]
    missing = setup.get("missing_labels") or []
    if missing:
        lines.append("Missing:")
        lines.extend([f"- {item}" for item in missing])
    return lines
