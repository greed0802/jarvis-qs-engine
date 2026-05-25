from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(payload: dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def new_contract_id() -> str:
    return f"contract_{uuid.uuid4().hex}"


class BuilderEngineContractSafety(BaseModel):
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False


class BuilderEngineSetupContract(BaseModel):
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


class BuilderEngineContractBlocker(BaseModel):
    code: str
    message: str
    fields: list[str] = Field(default_factory=list)


class BuilderEngineContractValidation(BaseModel):
    valid: bool = False
    blockers: list[BuilderEngineContractBlocker] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BuilderEngineContract(BaseModel):
    contract_id: str
    conversation_id: str
    task_id: str
    snapshot_id: str
    adapter_input_id: str | None = None
    source: Literal["builder_adapter_input", "builder_run_snapshot"] = "builder_adapter_input"
    engine_mode: Literal["contract_only"] = "contract_only"
    contract_schema_version: str = "builder_contract_v1"
    legacy_target: str = "legacy_builder_v4_contract_v1"
    engine_version_target: str = "legacy_builder_v4_contract_v1"
    contract_status: Literal["ready_for_engine_connection", "blocked"] = "ready_for_engine_connection"
    workbook_ref: dict[str, Any]
    builder_setup: BuilderEngineSetupContract
    setup_completeness: dict[str, Any] | None = None
    normalization: dict[str, Any] | None = None
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    safety: BuilderEngineContractSafety = Field(default_factory=BuilderEngineContractSafety)
    validation: BuilderEngineContractValidation = Field(default_factory=BuilderEngineContractValidation)
    contract_hash: str = ""
    created_at: str = Field(default_factory=now_iso)


def compute_contract_hash(contract: BuilderEngineContract) -> str:
    payload = contract.model_dump(mode="json")
    payload.pop("contract_hash", None)
    payload.pop("created_at", None)
    return canonical_hash(payload)
