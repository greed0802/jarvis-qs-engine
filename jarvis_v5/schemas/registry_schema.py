from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class RegistryRequirementCheckRequest(BaseModel):
    request: str


class RegistryRequirementCheckResponse(BaseModel):
    route: str = "registry_requirement_check"
    request: str
    matches: list[dict[str, Any]] = Field(default_factory=list)
    top_match: dict[str, Any] | None = None
    capability_candidates: list[str] = Field(default_factory=list)
    tool_candidates: list[str] = Field(default_factory=list)
    connector_candidates: list[str] = Field(default_factory=list)
    requires_clarification: bool = False
    risk_level: str = "low"
    requires_approval: bool = False
    advisory_type: str = "capability_advisory"
    advisory_route: str = "capability_advisory"
    builder_mutation_allowed: bool = False
    active_task_mutated: bool = False
    requires_file_read: bool = False
    future_tool_requested: bool = False
    execution_requested: bool = False
    execution_blocked: bool = False
    blocked_reason: str | None = None
    known_scope: bool | None = None
    unknown_scope: bool = False
    clarification_questions: list[str] = Field(default_factory=list)
    metadata_only: bool = True
    execution_enabled: bool = False
    all_entries_execution_disabled: bool = True
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    connector_called: bool = False
    model_called: bool = False
    install_command_run: bool = False
    tool_execution_called: bool = False
