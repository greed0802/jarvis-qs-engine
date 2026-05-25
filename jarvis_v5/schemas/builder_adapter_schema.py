from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BuilderAdapterInput(BaseModel):
    adapter_input_id: str
    conversation_id: str
    task_id: str
    snapshot_id: str
    snapshot_hash: str | None = None
    source: Literal["builder_run_snapshot"] = "builder_run_snapshot"
    workbook_ref: dict[str, Any] | None = None
    workbook_read: bool = False
    trade_profile: str | None = None
    costx_function: str | None = None
    custom_quantity: str | None = None
    unit: str | None = None
    zone_mode: str = "rebuild"
    dynamic_zones: list[dict[str, Any]] = Field(default_factory=list)
    heading_assignments: dict[str, Any] = Field(default_factory=dict)
    levels: list[str] = Field(default_factory=list)
    aliases: dict[str, Any] = Field(default_factory=dict)
    item_code_settings: dict[str, Any] = Field(default_factory=dict)
    trade_registry: dict[str, Any] | None = None
    setup_completeness: dict[str, Any] | None = None
    normalization: dict[str, Any] | None = None
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)


class BuilderAdapterValidation(BaseModel):
    valid_for_dry_run: bool = True
    valid_for_future_engine: bool = False
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BuilderAdapterDryRunResult(BaseModel):
    adapter_input_id: str
    conversation_id: str
    task_id: str
    snapshot_id: str
    snapshot_status: str
    route: str = "builder_adapter_dry_run"
    blocked: bool = False
    reason: str | None = None
    adapter_status: str = "dry_run_ready_with_warnings"
    freshness: Literal["current", "stale", "blocked"] = "current"
    stale_reason: str | None = None
    engine_called: bool = False
    excel_created: bool = False
    workbook_read: bool = False
    adapter_input: BuilderAdapterInput
    validation: BuilderAdapterValidation
    message: str
    setup_completeness: dict[str, Any] | None = None
    normalization: dict[str, Any] | None = None
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=now_iso)
    updated_at: str | None = None


def new_adapter_input_id() -> str:
    return f"adapter_{uuid.uuid4().hex}"
