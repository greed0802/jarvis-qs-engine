from __future__ import annotations

from typing import Any
from jarvis_v5.schemas.builder_adapter_schema import (
    BuilderAdapterDryRunResult,
    BuilderAdapterInput,
    BuilderAdapterValidation,
    new_adapter_input_id,
)
from jarvis_v5.schemas.builder_snapshot_schema import BuilderRunSnapshot
from jarvis_v5.tools.builder.setup_completeness import setup_completeness_from_snapshot
from jarvis_v5.parsers.conflict_guard import plan_normalization_report


def _missing_to_warnings(setup: dict[str, Any] | None) -> list[str]:
    missing = (setup or {}).get("missing_required") or []
    mapping = {
        "workbook_ref": "No workbook attached",
        "trade_profile": "No trade/profile selected",
        "costx_function": "No CostX function selected",
        "custom_quantity": "No custom quantity selected",
        "unit": "No unit selected",
        "dynamic_zones": "No dynamic zones set",
        "heading_assignments": "No heading assignments set",
        "levels": "No levels set",
        "pending_clarification": "Pending clarification exists",
        "snapshot_current": "Snapshot is not current",
        "adapter_current": "Adapter dry run is not current",
    }
    return [mapping.get(item, f"Missing {item}") for item in missing]


def _future_engine_warnings(adapter_input: BuilderAdapterInput) -> list[str]:
    warnings: list[str] = []
    if not adapter_input.workbook_ref:
        warnings.append("No workbook attached")
    if not adapter_input.trade_profile:
        warnings.append("No trade/profile selected")
    if not adapter_input.costx_function:
        warnings.append("No CostX function selected")
    if not adapter_input.unit:
        warnings.append("No unit selected")
    if adapter_input.zone_mode == "rebuild" and not adapter_input.dynamic_zones:
        warnings.append("No dynamic zones set")
    if adapter_input.zone_mode == "rebuild" and not adapter_input.heading_assignments:
        warnings.append("No heading assignments set")
    if not adapter_input.levels:
        warnings.append("No levels set")
    return warnings


def _future_engine_issues(adapter_input: BuilderAdapterInput) -> list[str]:
    issues: list[str] = []
    if not adapter_input.workbook_ref:
        issues.append("Missing workbook")
    if not adapter_input.trade_profile:
        issues.append("Missing trade/profile")
    if not adapter_input.costx_function:
        issues.append("Missing CostX function")
    if not adapter_input.unit:
        issues.append("Missing unit")
    if adapter_input.zone_mode == "rebuild" and not adapter_input.dynamic_zones:
        issues.append("Missing dynamic zones for rebuild mode")
    if adapter_input.zone_mode == "rebuild" and not adapter_input.heading_assignments:
        issues.append("Missing heading assignments for rebuild mode")
    if not adapter_input.levels:
        issues.append("Missing levels")

    dirty_markers = (" contains ", " use head", " levels", " preview", " export")
    for zone in adapter_input.dynamic_zones:
        for value in zone.get("values") or []:
            text = f" {str(value).strip().lower()}"
            if any(marker in text for marker in dirty_markers):
                issues.append(f"Suspicious zone value: {value}")
    return issues


def build_adapter_input_from_snapshot(*, snapshot: BuilderRunSnapshot) -> BuilderAdapterInput:
    return BuilderAdapterInput(
        adapter_input_id=new_adapter_input_id(),
        conversation_id=snapshot.conversation_id,
        task_id=snapshot.task_id,
        snapshot_id=snapshot.snapshot_id,
        snapshot_hash=snapshot.snapshot_hash,
        source="builder_run_snapshot",
        workbook_ref=snapshot.workbook_ref,
        workbook_read=False,
        trade_profile=snapshot.trade_profile,
        costx_function=snapshot.costx_function,
        custom_quantity=snapshot.custom_quantity,
        unit=snapshot.unit,
        zone_mode=snapshot.zone_mode,
        dynamic_zones=snapshot.dynamic_zones,
        heading_assignments=snapshot.heading_assignments,
        levels=snapshot.levels,
        aliases=snapshot.aliases,
        item_code_settings=snapshot.item_code_settings,
        trade_registry=getattr(snapshot, "trade_registry", None),
        setup_completeness=setup_completeness_from_snapshot(snapshot),
        normalization=getattr(snapshot, "normalization", None) or plan_normalization_report(snapshot.model_dump(mode="json") if hasattr(snapshot, "model_dump") else {}),
        conflicts=getattr(snapshot, "conflicts", []) or [],
    )


def run_builder_adapter_dry_run(*, snapshot: BuilderRunSnapshot) -> BuilderAdapterDryRunResult:
    adapter_input = build_adapter_input_from_snapshot(snapshot=snapshot)
    setup = adapter_input.setup_completeness or setup_completeness_from_snapshot(snapshot)
    future_issues = _future_engine_issues(adapter_input)
    warnings = _missing_to_warnings(setup) or _future_engine_warnings(adapter_input)
    validation = BuilderAdapterValidation(
        valid_for_dry_run=bool(setup.get("ready_for_dry_run", True)),
        valid_for_future_engine=bool(setup.get("ready_for_future_engine", False)) and not future_issues,
        issues=[],
        warnings=warnings,
    )
    status = "dry_run_ready" if validation.valid_for_future_engine else "dry_run_ready_with_warnings"
    message = "Builder adapter dry run completed. No Builder engine was called and no Excel file was created."
    if not validation.valid_for_future_engine:
        message += " Future engine readiness is not complete yet."
    return BuilderAdapterDryRunResult(
        adapter_input_id=adapter_input.adapter_input_id,
        conversation_id=snapshot.conversation_id,
        task_id=snapshot.task_id,
        snapshot_id=snapshot.snapshot_id,
        snapshot_status=snapshot.status,
        blocked=False,
        reason="builder_adapter_dry_run_completed",
        adapter_status=status,
        engine_called=False,
        excel_created=False,
        workbook_read=False,
        adapter_input=adapter_input,
        validation=validation,
        message=message,
        setup_completeness=setup,
        normalization=adapter_input.normalization,
        conflicts=adapter_input.conflicts,
    )


def adapter_trace_payload(result: BuilderAdapterDryRunResult | dict[str, Any] | None) -> dict[str, Any] | None:
    if result is None:
        return None
    if hasattr(result, "model_dump"):
        payload = result.model_dump(mode="json")
    else:
        payload = result
    validation = payload.get("validation") or {}
    return {
        "adapter_input_id": payload.get("adapter_input_id"),
        "snapshot_id": payload.get("snapshot_id"),
        "snapshot_status": payload.get("snapshot_status"),
        "freshness": payload.get("freshness", "current"),
        "stale_reason": payload.get("stale_reason"),
        "engine_called": bool(payload.get("engine_called", False)),
        "excel_created": bool(payload.get("excel_created", False)),
        "workbook_read": bool(payload.get("workbook_read", False)),
        "valid_for_dry_run": bool(validation.get("valid_for_dry_run", False)),
        "valid_for_future_engine": bool(validation.get("valid_for_future_engine", False)),
        "adapter_status": payload.get("adapter_status"),
        "setup_completeness": payload.get("setup_completeness"),
        "normalization": payload.get("normalization"),
        "conflicts": payload.get("conflicts") or [],
        "trade_registry": (payload.get("adapter_input") or {}).get("trade_registry") or payload.get("trade_registry"),
    }
