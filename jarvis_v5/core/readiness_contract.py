from __future__ import annotations

from typing import Any

NO_ENGINE_SAFETY = {
    "workbook_read": False,
    "engine_called": False,
    "excel_created": False,
    "contract_only": True,
    "legacy_builder_called": False,
}


def _missing_labels(setup: dict[str, Any] | None) -> list[str]:
    if not isinstance(setup, dict):
        return []
    return list(setup.get("missing_labels") or setup.get("missing_required") or [])


def _pending_prompt(task: Any | None = None, state: Any | None = None) -> str | None:
    pending = getattr(task, "pending_clarification", None) if task is not None else None
    if isinstance(pending, dict):
        return pending.get("prompt")
    return None


def build_readiness_contract(
    *,
    task: Any | None = None,
    state: Any | None = None,
    setup: dict[str, Any] | None = None,
    snapshot: dict[str, Any] | None = None,
    adapter: dict[str, Any] | None = None,
    engine_contract: dict[str, Any] | None = None,
    engine_boundary_audit: dict[str, Any] | None = None,
    normalization: dict[str, Any] | None = None,
    conflicts: list[Any] | None = None,
    workbook_read_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Read-only alpha.15 readiness summary.

    This helper never mutates Builder state and never calls workbook/engine logic.
    It only summarizes existing state already loaded by the API/router.
    """
    setup = setup or {}
    snapshot = snapshot or {}
    adapter = adapter or {}
    engine_contract = engine_contract or {}
    engine_boundary_audit = engine_boundary_audit or {}
    normalization = normalization or {}
    conflicts = list(conflicts or [])
    workbook_read_policy = workbook_read_policy or {}
    policy_reviewed = workbook_read_policy.get("status") == "reviewed"

    pending_id = getattr(state, "pending_clarification_id", None) if state is not None else None
    pending_open = bool(pending_id or getattr(task, "pending_clarification", None))
    workbook_attached = bool(getattr(task, "workbook", None)) if task is not None else False
    ready_future = bool(setup.get("ready_for_future_engine"))
    missing = list(setup.get("missing_required") or [])
    blockers: list[dict[str, Any]] = []

    snapshot_found = bool(snapshot.get("found", True) and snapshot.get("snapshot_id")) if snapshot else False
    snapshot_current = bool(snapshot_found and snapshot.get("status") == "current")
    snapshot_stale = bool(snapshot_found and snapshot.get("status") == "stale")

    adapter_found = bool(adapter.get("found", True) and adapter.get("adapter_input_id")) if adapter else False
    adapter_current = bool(adapter_found and adapter.get("freshness", "current") == "current")
    adapter_ready = bool(adapter_found and adapter_current and adapter.get("valid_for_future_engine"))

    contract_found = bool(engine_contract.get("found") and engine_contract.get("contract_id"))
    contract_ready = bool(contract_found and engine_contract.get("status") == "ready_for_engine_connection")

    if pending_open:
        blockers.append({
            "code": "pending_clarification_exists",
            "message": "Answer or cancel the pending clarification before creating a snapshot, adapter dry run, or engine contract.",
            "fields": ["pending_clarification"],
        })
    if conflicts:
        blockers.append({
            "code": "unresolved_conflicts",
            "message": "Resolve setup conflicts before continuing.",
            "fields": ["conflicts"],
        })
    if snapshot_stale:
        blockers.append({
            "code": "snapshot_is_stale",
            "message": "Create a new snapshot from the current Builder plan.",
            "fields": ["snapshot"],
        })
    if adapter_found and not adapter_current:
        blockers.append({
            "code": "adapter_is_stale",
            "message": "Run adapter dry run again after creating a current snapshot.",
            "fields": ["adapter_dry_run"],
        })

    if pending_open:
        status = "needs_clarification"
        user_status = "Blocked by open clarification"
    elif contract_ready:
        status = "contract_ready"
        user_status = "Ready for future engine connection"
    elif adapter_ready:
        status = "ready_for_contract"
        user_status = "Ready to create safe engine contract"
    elif snapshot_current:
        status = "snapshot_current"
        user_status = "Ready for adapter dry run"
    elif ready_future:
        status = "ready_for_snapshot"
        user_status = "Ready to create snapshot"
    elif not workbook_attached:
        status = "waiting_for_workbook" if task is not None else "not_started"
        user_status = "Waiting for workbook" if task is not None else "No active Builder task"
    else:
        status = "incomplete_setup"
        user_status = "Setup incomplete"

    blocked = bool(blockers) or status in {"needs_clarification", "incomplete_setup", "waiting_for_workbook", "not_started"}
    can_create_snapshot = bool(ready_future and not pending_open and not conflicts)
    can_run_adapter = bool(snapshot_current and not pending_open and not conflicts)
    can_create_contract = bool(adapter_ready and not pending_open and not conflicts)

    next_actions: list[str] = []
    if pending_open:
        next_actions.append("Answer or cancel the clarification")
    elif not workbook_attached and task is not None:
        next_actions.append("Attach workbook")
    elif missing:
        next_actions.extend([f"Set {label}" for label in _missing_labels(setup)])
    elif not snapshot_current:
        next_actions.append("Create snapshot")
    elif not adapter_ready:
        next_actions.append("Run adapter dry run")
    elif not contract_ready:
        next_actions.append("Create engine contract")
    else:
        next_actions.append("Review contract/debug output; Preview and Export remain stubbed")

    return {
        "status": status,
        "user_status": user_status,
        "can_create_snapshot": can_create_snapshot,
        "can_run_adapter_dry_run": can_run_adapter,
        "can_create_engine_contract": can_create_contract,
        "can_preview": False,
        "can_export": False,
        "preview_status": "stubbed_no_engine",
        "export_status": "stubbed_no_engine",
        "blocked": blocked,
        "blockers": blockers,
        "missing": missing,
        "missing_labels": _missing_labels(setup),
        "next_actions": next_actions,
        "pending_clarification_id": pending_id,
        "pending_clarification_prompt": _pending_prompt(task, state),
        "setup_status": setup.get("status"),
        "snapshot_status": snapshot.get("status") if snapshot_found else None,
        "adapter_status": adapter.get("status") or adapter.get("adapter_status") if adapter_found else None,
        "adapter_freshness": adapter.get("freshness") if adapter_found else None,
        "engine_contract_status": engine_contract.get("status") if contract_found else None,
        "engine_boundary_audit_status": (engine_boundary_audit or {}).get("audit_status"),
        "normalization_status": normalization.get("status"),
        "trade_registry": normalization.get("trade_registry"),
        "workbook_read_policy_status": workbook_read_policy.get("status") or "not_reviewed",
        "workbook_read_policy_reviewed": bool(policy_reviewed),
        "workbook_read_policy": {
            "found": bool(workbook_read_policy.get("found")),
            "status": workbook_read_policy.get("status") or "not_reviewed",
            "policy_only": bool(workbook_read_policy.get("policy_only", True)),
            "workbook_opened": False,
            "workbook_read": False,
            "workbook_content_read": False,
            "cells_read": False,
            "formulas_read": False,
            "engine_called": False,
            "excel_created": False,
            "legacy_builder_called": False,
        },
        "safety": dict(NO_ENGINE_SAFETY),
    }


def build_review_message(
    *,
    plan_summary: dict[str, Any] | None = None,
    workbook: dict[str, Any] | None = None,
    setup: dict[str, Any] | None = None,
    readiness: dict[str, Any] | None = None,
    normalization: dict[str, Any] | None = None,
    snapshot: dict[str, Any] | None = None,
    adapter: dict[str, Any] | None = None,
    engine_contract: dict[str, Any] | None = None,
    engine_preflight: dict[str, Any] | None = None,
    engine_execution: dict[str, Any] | None = None,
) -> str:
    plan_summary = plan_summary or {}
    workbook = workbook or {}
    setup = setup or {}
    readiness = readiness or {}
    normalization = normalization or {}
    snapshot = snapshot or {}
    adapter = adapter or {}
    engine_contract = engine_contract or {}
    engine_preflight = engine_preflight or {}
    engine_execution = engine_execution or {}

    lines: list[str] = ["Current Builder shell task", "Builder setup review", ""]
    lines.append("Current task: builder")
    lines.append(f"Status: {readiness.get('user_status') or readiness.get('status') or 'unknown'}")
    future_ready = readiness.get("status") == "contract_ready"
    lines.append(f"Future engine: {'ready' if future_ready else 'not ready'}")
    if readiness.get("pending_clarification_prompt"):
        lines.extend(["", "Open clarification:", str(readiness.get("pending_clarification_prompt"))])

    lines.extend(["", "Current setup:"])
    lines.append(f"- Workbook: {workbook.get('filename') if workbook.get('found') else 'not attached'}")
    lines.append(f"- Trade/Profile: {plan_summary.get('trade_profile') or 'not set'}")
    lines.append(f"- Function: {plan_summary.get('costx_function') or 'not set'}")
    if plan_summary.get("custom_quantity"):
        lines.append(f"- Custom quantity: {plan_summary.get('custom_quantity')}")
    lines.append(f"- Unit: {plan_summary.get('unit') or 'not set'}")
    zones = plan_summary.get("zones") or []
    if zones:
        zone_bits = []
        for zone in zones:
            values = ", ".join(zone.get("values") or [])
            head = zone.get("head_assignment") or "no head"
            zone_bits.append(f"Zone {zone.get('zone_id')}: {values} ({head})")
        lines.append(f"- Zones: {'; '.join(zone_bits)}")
    else:
        lines.append("- Zones: not set")
    levels = plan_summary.get("levels") or []
    lines.append(f"- Levels: {', '.join(levels) if levels else 'not set'}")

    registry = plan_summary.get("trade_registry") or normalization.get("trade_registry")
    if registry:
        lines.extend(["", "Trade registry:"])
        lines.append(f"- Match: {registry.get('registry_key') or registry.get('input')}")
        lines.append(f"- Canonical trade: {registry.get('canonical_trade')}")
        lines.append(f"- Mode: {registry.get('normalization_mode')}")
        lines.append(f"- Requires clarification: {'yes' if registry.get('requires_clarification') else 'no'}")

    lines.extend(["", "Setup completeness", f"Status: {setup.get('status') or 'unknown'}"])
    if setup.get("missing_labels"):
        lines.extend(["Missing:"])
        lines.extend([f"- {item}" for item in setup.get("missing_labels") or []])
    else:
        lines.append("Missing: none")

    if snapshot.get("found") or snapshot.get("snapshot_id"):
        lines.extend(["", "Snapshot:", f"- Status: {snapshot.get('status')}"])
    if adapter.get("found") or adapter.get("adapter_input_id"):
        lines.extend(["", "Builder Adapter Dry Run", f"- Status: {adapter.get('status') or adapter.get('adapter_status')}", f"- Freshness: {adapter.get('freshness')}"])
        if adapter.get("freshness") == "stale":
            lines.append("Action needed: Create a new Builder snapshot, then run adapter dry run again.")
    if engine_contract.get("found") or engine_contract.get("contract_id"):
        lines.extend(["", "Engine contract:", f"- Status: {engine_contract.get('status')}", f"- Contract ID: {engine_contract.get('contract_id')}", f"- Schema: {engine_contract.get('contract_schema_version')}", f"- Legacy target: {engine_contract.get('legacy_target')}"])

    if engine_preflight.get("found"):
        lines.extend(["", "Builder engine preflight:"])
        lines.append(f"- Status: {engine_preflight.get('status')}")
        lines.append(f"- Contract: {engine_preflight.get('contract_schema_version')}")
        lines.append(f"- Legacy target: {engine_preflight.get('legacy_target')}")
        lines.append(f"- Compatibility: {engine_preflight.get('compatibility_score')}%")
        missing_preflight = engine_preflight.get("missing_required_fields") or []
        lines.append(f"- Missing required fields: {', '.join(missing_preflight) if missing_preflight else 'none'}")

    if engine_execution.get("found"):
        lines.extend(["", "Builder engine execution lock:"])
        lines.append(f"- Status: {engine_execution.get('status')}")
        lines.append(f"- Reason: {engine_execution.get('reason') or 'none'}")
        lines.append(f"- Execution enabled: {'yes' if engine_execution.get('execution_enabled') else 'no'}")
        lines.append(f"- Legacy target: {engine_execution.get('legacy_target') or 'legacy_builder_v4_contract_v1'}")
        lines.append("- Execution: blocked by kill switch")

    lines.extend(["", "Next safe action:"])
    lines.extend([f"- {item}" for item in readiness.get("next_actions") or ["Continue setup"]])

    lines.extend(["", "Preview/Export:", "Preview/export engines are not connected in this alpha.", "No Builder engine is connected."])
    safety = readiness.get("safety") or NO_ENGINE_SAFETY
    lines.extend(["", "Safety:"])
    lines.append("No workbook was read. No Builder engine was called. No Excel file was created.")
    lines.append(f"contract_only={str(safety.get('contract_only')).lower()}, legacy_builder_called={str(safety.get('legacy_builder_called')).lower()}")
    return "\n".join(lines)
