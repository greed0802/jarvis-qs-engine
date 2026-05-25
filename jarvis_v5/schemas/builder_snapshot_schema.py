from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field
from jarvis_v5.tools.builder.setup_completeness import setup_completeness_from_plan
from jarvis_v5.parsers.conflict_guard import plan_normalization_report


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(payload: dict[str, Any]) -> str:
    """Stable hash for snapshot proof/debugging.

    Alpha.4.1 uses this only as a frozen-state proof. It does not run Builder.
    """
    normalized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


PLAN_HASH_FIELDS = [
    "trade_profile",
    "costx_function",
    "custom_quantity",
    "unit",
    "zone_mode",
    "dynamic_zones",
    "heading_assignments",
    "levels",
    "aliases",
    "item_code_settings",
    "trade_registry",
]


def stable_plan_payload(plan: dict[str, Any] | None) -> dict[str, Any]:
    """Return only stable Builder plan fields used to judge snapshot freshness."""
    plan = plan or {}
    payload: dict[str, Any] = {}
    for key in PLAN_HASH_FIELDS:
        value = plan.get(key)
        if value is None:
            if key in {"dynamic_zones", "levels"}:
                value = []
            elif key in {"heading_assignments", "aliases", "item_code_settings"}:
                value = {}
        payload[key] = value
    return payload


def plan_hash_from_plan(plan: dict[str, Any] | None) -> str:
    return canonical_hash(stable_plan_payload(plan))


class SnapshotValidation(BaseModel):
    valid: bool = True
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    setup_completeness: dict[str, Any] | None = None


class BuilderRunSnapshot(BaseModel):
    snapshot_id: str
    conversation_id: str
    task_id: str
    source: Literal["active_task"] = "active_task"
    workbook_ref: dict[str, Any] | None = None
    trade_profile: str | None = None
    costx_function: str | None = None
    custom_quantity: str | None = None
    unit: str | None = None
    zone_mode: Literal["rebuild", "preserve_source"] = "rebuild"
    dynamic_zones: list[dict[str, Any]] = Field(default_factory=list)
    heading_assignments: dict[str, Any] = Field(default_factory=dict)
    levels: list[str] = Field(default_factory=list)
    aliases: dict[str, Any] = Field(default_factory=dict)
    item_code_settings: dict[str, Any] = Field(default_factory=dict)
    trade_registry: dict[str, Any] | None = None
    approved_by_user: bool = True
    status: Literal["current", "stale", "superseded"] = "current"
    stale_reason: str | None = None
    source_plan_hash: str = ""
    active_plan_hash: str | None = None
    validation: SnapshotValidation = Field(default_factory=SnapshotValidation)
    setup_completeness: dict[str, Any] | None = None
    normalization: dict[str, Any] | None = None
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    snapshot_hash: str = ""
    created_at: str = Field(default_factory=now_iso)
    updated_at: str | None = None


def validate_snapshot_from_plan(*, task_status: str | None, workbook_ref: dict[str, Any] | None, plan: dict[str, Any]) -> SnapshotValidation:
    """Alpha.4.1 skeleton validation.

    Only structural state errors block snapshot creation. Missing production Builder
    requirements are warnings until a real Builder engine is connected.
    """
    issues: list[str] = []
    warnings: list[str] = []
    if task_status == "cancelled":
        issues.append("Active task is cancelled")
    if not isinstance(plan, dict) or not plan:
        issues.append("Active Builder plan is missing")

    setup = setup_completeness_from_plan(plan=plan, workbook_ref=workbook_ref, pending_clarification=False)
    if not workbook_ref:
        warnings.append("No workbook attached")
    if not plan.get("trade_profile"):
        warnings.append("No trade/profile selected")
    if not plan.get("costx_function"):
        warnings.append("No CostX function selected")
    if not plan.get("unit"):
        warnings.append("No unit selected")
    if not plan.get("levels"):
        warnings.append("No levels set")
    if not plan.get("dynamic_zones"):
        warnings.append("No dynamic zones set")
    if plan.get("zone_mode", "rebuild") == "rebuild" and not plan.get("heading_assignments"):
        warnings.append("No heading assignments set")
    if "function_unit_compatibility" in (setup.get("missing_required") or []):
        issues.append("Function/unit compatibility conflict")

    return SnapshotValidation(valid=not issues, issues=issues, warnings=warnings, setup_completeness=setup)


def build_snapshot_from_active_task(*, snapshot_id: str, conversation_id: str, task: Any, approve: bool = True) -> BuilderRunSnapshot:
    plan = task.plan or {}
    validation = validate_snapshot_from_plan(task_status=task.status, workbook_ref=task.workbook, plan=plan)
    source_plan_hash = plan_hash_from_plan(plan)
    snapshot = BuilderRunSnapshot(
        snapshot_id=snapshot_id,
        conversation_id=conversation_id,
        task_id=task.task_id,
        source="active_task",
        workbook_ref=task.workbook,
        trade_profile=plan.get("trade_profile"),
        costx_function=plan.get("costx_function"),
        custom_quantity=plan.get("custom_quantity"),
        unit=plan.get("unit"),
        zone_mode=plan.get("zone_mode") or "rebuild",
        dynamic_zones=plan.get("dynamic_zones") or [],
        heading_assignments=plan.get("heading_assignments") or {},
        levels=plan.get("levels") or [],
        aliases=plan.get("aliases") or {},
        item_code_settings=plan.get("item_code_settings") or {},
        trade_registry=plan.get("trade_registry"),
        approved_by_user=bool(approve),
        status="current",
        stale_reason=None,
        source_plan_hash=source_plan_hash,
        active_plan_hash=source_plan_hash,
        validation=validation,
        setup_completeness=validation.setup_completeness,
        normalization=plan_normalization_report(plan),
        conflicts=[],
    )
    hash_payload = snapshot.model_dump(mode="json")
    hash_payload.pop("snapshot_hash", None)
    hash_payload.pop("created_at", None)
    hash_payload.pop("updated_at", None)
    snapshot.snapshot_hash = canonical_hash(hash_payload)
    return snapshot
