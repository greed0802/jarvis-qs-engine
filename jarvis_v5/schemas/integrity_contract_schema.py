from __future__ import annotations

from pydantic import BaseModel, Field


class IntegritySafetyEnvelope(BaseModel):
    metadata_only: bool = True
    execution_enabled: bool = False
    workbook_read: bool = False
    workbook_content_read: bool = False
    sheet_name_probe_allowed: bool = False
    formula_read: bool = False
    cell_value_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False


class ExecutionTierSpec(BaseModel):
    tier_key: str
    tier: int
    display_name: str
    allowed_in_alpha36_0: bool = False
    future_only: bool = True
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: IntegritySafetyEnvelope = Field(default_factory=IntegritySafetyEnvelope)


class ToolRiskTierSpec(BaseModel):
    tool_key: str
    risk_tier: int
    risk_name: str
    future_only: bool = True
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: IntegritySafetyEnvelope = Field(default_factory=IntegritySafetyEnvelope)


class StateTransitionSpec(BaseModel):
    from_state: str
    to_state: str
    allowed: bool = False
    blocked_reason: str | None = None
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: IntegritySafetyEnvelope = Field(default_factory=IntegritySafetyEnvelope)


class ApprovalEscalationSpec(BaseModel):
    approval_level: str
    risk_tier_required: int = 0
    future_only: bool = True
    grants_runtime_permission: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: IntegritySafetyEnvelope = Field(default_factory=IntegritySafetyEnvelope)


class BlockedTransitionSpec(BaseModel):
    transition_key: str
    from_state: str
    to_state: str
    blocked_reason: str
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: IntegritySafetyEnvelope = Field(default_factory=IntegritySafetyEnvelope)


class AuditEventRequirementSpec(BaseModel):
    event_type: str
    required_fields: list[str] = Field(default_factory=list)
    writes_runtime_event: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety_snapshot: IntegritySafetyEnvelope = Field(default_factory=IntegritySafetyEnvelope)


class FutureToolRollbackPolicySpec(BaseModel):
    tool_key: str
    rollback_policy_key: str
    source_files_untouched: bool = True
    destructive_delete_allowed: bool = False
    output_only: bool = True
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: IntegritySafetyEnvelope = Field(default_factory=IntegritySafetyEnvelope)


class ReadinessGateSpec(BaseModel):
    gate_key: str
    description: str
    required_before_sheet_name_probe: bool = True
    satisfied_in_alpha36_0: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: IntegritySafetyEnvelope = Field(default_factory=IntegritySafetyEnvelope)


class IntegrityContractMapResponse(BaseModel):
    version: str
    route: str = "pre_execution_integrity_contract_metadata_only"
    execution_tiers: list[ExecutionTierSpec] = Field(default_factory=list)
    tool_risk_tiers: list[ToolRiskTierSpec] = Field(default_factory=list)
    state_transitions: list[StateTransitionSpec] = Field(default_factory=list)
    blocked_transitions: list[BlockedTransitionSpec] = Field(default_factory=list)
    readiness_gates: list[ReadinessGateSpec] = Field(default_factory=list)
    metadata_only: bool = True
    execution_enabled: bool = False
    workbook_read: bool = False
    workbook_content_read: bool = False
    sheet_name_probe_allowed: bool = False
    formula_read: bool = False
    cell_value_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False
