from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class AttachmentMeta(BaseModel):
    attachment_id: str | None = None
    filename: str
    content_type: str | None = None
    size_bytes: int | None = None
    saved_path: str | None = None


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    text: str = ""
    client_event_id: str | None = None
    mode: Literal["ask_first", "autopilot", "manual"] = "ask_first"
    attachments: list[AttachmentMeta] = Field(default_factory=list)


class ChatResponse(BaseModel):
    conversation_id: str
    event_id: str
    intent: str
    route: str
    message: str
    active_task_id: str | None = None
    active_task_status: str | None = None
    pending_clarification_id: str | None = None
    blocked: bool = False
    reason: str | None = None
    router_step: str | None = None
    duplicate: bool = False
    state: dict[str, Any] = Field(default_factory=dict)
    reducer_result: dict[str, Any] | None = None
    snapshot: dict[str, Any] | None = None
    adapter: dict[str, Any] | None = None
    setup_completeness: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None
    clarification_resolved: bool | None = None
    route_confidence: int | None = None
    confidence_reason: str | None = None
    tool_candidates: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    requires_clarification: bool = False
    confidence_engine: dict[str, Any] | None = None
    route_context: dict[str, Any] | None = None
    capability_candidates: list[str] = Field(default_factory=list)
    registry_assist: dict[str, Any] | None = None
    requirement_advisor: dict[str, Any] | None = None
    registry_advisory: dict[str, Any] | None = None
    non_mutating_category: str | None = None
    active_task_action_language: dict[str, Any] | None = None
    plan_mutated: bool | None = None
    metadata_only: bool | None = None
    execution_enabled: bool | None = None
    policy_only: bool | None = None
    current_access_tier: str | None = None
    current_allowed_operations: list[str] | None = None
    current_blocked_operations: list[str] | None = None
    future_access_tiers: list[dict[str, Any]] | None = None
    required_future_approval_gates: list[str] | None = None
    blocked_by_policy: list[str] | None = None
    cell_read_enabled: bool | None = None
    formula_read_enabled: bool | None = None
    dimension_read_enabled: bool | None = None
    workbook_parse_enabled: bool | None = None
    workbook_opened: bool | None = None
    workbook_read: bool | None = None
    workbook_content_read: bool | None = None
    workbook_parsed: bool | None = None
    cells_read: bool | None = None
    formulas_read: bool | None = None
    engine_called: bool | None = None
    excel_created: bool | None = None
    contract_only: bool | None = None
    legacy_builder_called: bool | None = None
    preview_readiness_upgraded: bool | None = None
    export_readiness_upgraded: bool | None = None
    next_safe_action: str | None = None
    safety: dict[str, Any] | None = None


class DebugClarificationRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    prompt: str = "Choose A or B."
    options: list[str] = Field(default_factory=lambda: ["A", "B", "Cancel"])


class DebugClarificationResponse(BaseModel):
    conversation_id: str
    active_task_id: str | None = None
    pending_clarification_id: str | None = None
    route: str
    message: str
    status: str | None = None
    blocked: bool = False
    reason: str | None = None
    router_step: str | None = None
    intent: str | None = None
    state: dict[str, Any] = Field(default_factory=dict)
    reducer_result: dict[str, Any] | None = None
    snapshot: dict[str, Any] | None = None
    setup_completeness: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None
    safety: dict[str, Any] = Field(default_factory=dict)

class SnapshotCreateRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    approve: bool = True


class SnapshotCreateResponse(BaseModel):
    conversation_id: str
    active_task_id: str | None = None
    snapshot_id: str | None = None
    route: str
    message: str
    valid: bool = False
    blocked: bool = False
    reason: str | None = None
    router_step: str | None = None
    snapshot_hash: str | None = None
    snapshot_status: str | None = None
    stale_reason: str | None = None
    source_plan_hash: str | None = None
    active_plan_hash: str | None = None
    validation: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    snapshot: dict[str, Any] | None = None
    setup_completeness: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)


class BuilderAdapterDryRunRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    snapshot_id: str | None = None
    allow_stale: bool = False


class BuilderAdapterDryRunResponse(BaseModel):
    conversation_id: str
    active_task_id: str | None = None
    snapshot_id: str | None = None
    adapter_input_id: str | None = None
    route: str
    message: str
    blocked: bool = False
    reason: str | None = None
    router_step: str | None = None
    adapter_status: str | None = None
    engine_called: bool = False
    excel_created: bool = False
    workbook_read: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    adapter_input: dict[str, Any] | None = None
    validation: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    snapshot: dict[str, Any] | None = None
    adapter: dict[str, Any] | None = None
    adapter_dry_run: dict[str, Any] | None = None
    setup_completeness: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None



class BuilderEngineContractRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    snapshot_id: str | None = None
    adapter_input_id: str | None = None
    allow_stale: bool = False


class BuilderEngineContractResponse(BaseModel):
    conversation_id: str
    active_task_id: str | None = None
    snapshot_id: str | None = None
    adapter_input_id: str | None = None
    contract_id: str | None = None
    route: str
    message: str
    contract_created: bool = False
    pending_clarification_id: str | None = None
    missing_required: list[str] = Field(default_factory=list)
    replay_url: str | None = None
    blocked: bool = False
    reason: str | None = None
    router_step: str | None = None
    contract_status: str | None = None
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    contract: dict[str, Any] | None = None
    validation: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    snapshot: dict[str, Any] | None = None
    adapter: dict[str, Any] | None = None
    engine_contract: dict[str, Any] | None = None
    setup_completeness: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None


class BuilderEnginePreflightRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    export_fixture: bool = True


class BuilderEnginePreflightResponse(BaseModel):
    conversation_id: str
    contract_id: str | None = None
    preflight_id: str | None = None
    route: str
    message: str
    blocked: bool = False
    reason: str | None = None
    preflight_status: str | None = None
    contract_schema_version: str | None = None
    legacy_target: str | None = None
    compatibility: dict[str, Any] = Field(default_factory=dict)
    safety: dict[str, Any] = Field(default_factory=dict)
    fixture_path: str | None = None
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    contract: dict[str, Any] | None = None
    engine_boundary_audit: dict[str, Any] | None = None
    validation: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] | None = None




class PreviewExecutionPolicyRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    requested_action: Literal["preview", "export"] = "preview"


class PreviewExecutionPolicyResponse(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    policy_id: str | None = None
    route: str
    message: str
    metadata_only: bool = True
    execution_enabled: bool = False
    blocked: bool = True
    reason: str | None = None
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    requested_action: str = "preview"
    contract_found: bool = False
    contract_id: str | None = None
    contract_ready: bool = False
    policy_version: str | None = None
    blocked_by_policy: list[str] = Field(default_factory=list)
    execution_locks: dict[str, Any] = Field(default_factory=dict)
    workbook_read_permission_boundary: dict[str, Any] = Field(default_factory=dict)
    safe_workbook_path_resolver: dict[str, Any] = Field(default_factory=dict)
    preview_approval_policy: dict[str, Any] = Field(default_factory=dict)
    export_approval_policy: dict[str, Any] = Field(default_factory=dict)
    preview_result_schema: dict[str, Any] = Field(default_factory=dict)
    output_manifest_schema: dict[str, Any] = Field(default_factory=dict)
    background_job_boundary: dict[str, Any] = Field(default_factory=dict)
    formula_integrity_guard_connection_point: dict[str, Any] = Field(default_factory=dict)
    failure_recovery_contract: dict[str, Any] = Field(default_factory=dict)
    contract: dict[str, Any] | None = None
    contract_summary: dict[str, Any] | None = None
    approval_token_policy: dict[str, Any] = Field(default_factory=dict)
    preview_approval_readiness: dict[str, Any] = Field(default_factory=dict)
    export_approval_readiness: dict[str, Any] = Field(default_factory=dict)
    blocked_reason_details: list[dict[str, Any]] = Field(default_factory=list)
    readiness: dict[str, Any] | None = None
    next_safe_action: str | None = None


class SafeWorkbookPathResolverDryRunRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None


class SafeWorkbookPathResolverDryRunResponse(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    route: str
    message: str
    metadata_only: bool = True
    execution_enabled: bool = False
    blocked: bool = True
    reason: str | None = None
    contract_found: bool = False
    workbook_ref_found: bool = False
    workbook_ref_summary: dict[str, Any] = Field(default_factory=dict)
    jarvis_metadata_store_read: bool = False
    path_resolved: bool = False
    filesystem_checked: bool = False
    workbook_filesystem_checked: bool = False
    workbook_opened: bool = False
    raw_saved_path_present: bool = False
    path_like_metadata_present: bool = False
    raw_path_value_returned: bool = False
    forbidden_path_key_returned: bool = False
    raw_path_returned: bool = False
    raw_path_like_key_returned: bool = False
    filesystem_check_required_later: bool = True
    would_require_attachment_root_check_later: bool = True
    blocked_by_policy: list[str] = Field(default_factory=list)
    path_safety_summary: dict[str, Any] = Field(default_factory=dict)
    future_required_checks: list[str] = Field(default_factory=list)
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] | None = None
    next_safe_action: str | None = None


class WorkbookReadPreflightDryRunRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None


class WorkbookReadPreflightDryRunResponse(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    route: str
    message: str
    metadata_only: bool = True
    preflight_only: bool = True
    execution_enabled: bool = False
    blocked: bool = True
    reason: str | None = None
    contract_found: bool = False
    workbook_ref_found: bool = False
    path_resolver_contract_available: bool = False
    workbook_metadata_valid: bool = False
    workbook_metadata_complete: bool = False
    workbook_candidate_metadata_complete: bool = False
    workbook_candidate_allowed_by_metadata: bool = False
    workbook_read_allowed: bool = False
    workbook_open_allowed: bool = False
    filename: str | None = None
    workbook_id: str | None = None
    attachment_id: str | None = None
    source: str | None = None
    content_type: str | None = None
    content_type_allowed: bool = False
    size_bytes: int | None = None
    size_valid: bool = False
    extension: str | None = None
    extension_allowed: bool = False
    allowed_extensions: list[str] = Field(default_factory=list)
    rejected_extensions: list[str] = Field(default_factory=list)
    blocked_by_policy: list[str] = Field(default_factory=list)
    metadata_validation: dict[str, Any] = Field(default_factory=dict)
    future_required_checks: list[str] = Field(default_factory=list)
    path_resolver_summary: dict[str, Any] = Field(default_factory=dict)
    workbook_opened: bool = False
    workbook_read: bool = False
    workbook_parsed: bool = False
    sheet_names_read: bool = False
    cells_read: bool = False
    formulas_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    raw_path_value_returned: bool = False
    forbidden_path_key_returned: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    preflight_safety_summary: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] | None = None
    next_safe_action: str | None = None


class WorkbookMetadataProbeApprovalRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    approval_granted: bool = False


class WorkbookMetadataProbeApprovalResponse(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    route: str
    message: str
    metadata_only: bool = True
    execution_enabled: bool = False
    approval_required: bool = True
    approval_granted: bool = False
    blocked: bool = True
    reason: str | None = None
    contract_found: bool = False
    workbook_ref_found: bool = False
    allowed_metadata_fields: list[str] = Field(default_factory=list)
    blocked_operations: list[str] = Field(default_factory=list)
    blocked_by_policy: list[str] = Field(default_factory=list)
    workbook_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata_validation: dict[str, Any] = Field(default_factory=dict)
    workbook_opened: bool = False
    workbook_read: bool = False
    workbook_parsed: bool = False
    sheet_names_read: bool = False
    cells_read: bool = False
    formulas_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    raw_path_value_returned: bool = False
    forbidden_path_key_returned: bool = False
    preview_readiness_upgraded: bool = False
    export_readiness_upgraded: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] | None = None
    next_safe_action: str | None = None


class WorkbookSheetNameProbeApprovalRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    approval_granted: bool = False


class WorkbookSheetNameProbeApprovalResponse(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    route: str
    message: str
    approval_required: bool = True
    approval_granted: bool = False
    blocked: bool = True
    reason: str | None = None
    contract_found: bool = False
    workbook_ref_found: bool = False
    workbook_opened: bool = False
    workbook_closed: bool = False
    limited_metadata_read: bool = False
    sheet_names_read: bool = False
    sheet_names: list[str] = Field(default_factory=list)
    sheet_count: int = 0
    workbook_read: bool = False
    workbook_content_read: bool = False
    workbook_parsed: bool = False
    cells_read: bool = False
    formulas_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    raw_path_value_returned: bool = False
    forbidden_path_key_returned: bool = False
    preview_readiness_upgraded: bool = False
    export_readiness_upgraded: bool = False
    blocked_by_policy: list[str] = Field(default_factory=list)
    allowed_probe_fields: list[str] = Field(default_factory=list)
    blocked_operations: list[str] = Field(default_factory=list)
    safety: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] | None = None
    next_safe_action: str | None = None


class WorkbookReadPolicyReviewRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None


class WorkbookReadPolicyReviewResponse(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    route: str
    message: str
    policy_only: bool = True
    current_access_tier: str
    current_allowed_operations: list[str] = Field(default_factory=list)
    current_blocked_operations: list[str] = Field(default_factory=list)
    future_access_tiers: list[dict[str, Any]] = Field(default_factory=list)
    required_future_approval_gates: list[str] = Field(default_factory=list)
    blocked_by_policy: list[str] = Field(default_factory=list)
    cell_read_enabled: bool = False
    formula_read_enabled: bool = False
    dimension_read_enabled: bool = False
    workbook_parse_enabled: bool = False
    workbook_opened: bool = False
    workbook_read: bool = False
    workbook_content_read: bool = False
    workbook_parsed: bool = False
    cells_read: bool = False
    formulas_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    preview_readiness_upgraded: bool = False
    export_readiness_upgraded: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] | None = None
    next_safe_action: str | None = None


class BuilderEngineExecutionRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    preflight_id: str | None = None


class BuilderEngineExecutionResponse(BaseModel):
    conversation_id: str
    execution_request_id: str | None = None
    contract_id: str | None = None
    preflight_id: str | None = None
    route: str
    message: str
    blocked: bool = True
    reason: str | None = None
    execution_status: str | None = None
    bridge_status: str | None = None
    execution_enabled: bool = False
    legacy_target: str | None = None
    contract_schema_version: str | None = None
    would_call: dict[str, Any] = Field(default_factory=dict)
    compatibility: dict[str, Any] = Field(default_factory=dict)
    safety: dict[str, Any] = Field(default_factory=dict)
    execution_locks: dict[str, Any] = Field(default_factory=dict)
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    validation: dict[str, Any] = Field(default_factory=dict)
    readiness: dict[str, Any] | None = None


class BuilderEngineBoundaryAuditRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None


class BuilderEngineBoundaryAuditResponse(BaseModel):
    conversation_id: str
    contract_id: str | None = None
    route: str
    message: str
    blocked: bool = False
    reason: str | None = None
    audit_status: str | None = None
    contract_schema_version: str | None = None
    legacy_target: str | None = None
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    mapping: dict[str, Any] = Field(default_factory=dict)
    unmapped_contract_fields: list[str] = Field(default_factory=list)
    missing_legacy_required_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    validation: dict[str, Any] = Field(default_factory=dict)
    contract: dict[str, Any] | None = None
    engine_boundary_audit: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None

class LegacyBridgeShadowProbeRequest(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    contract_id: str | None = None
    allow_missing_contract: bool = True


class LegacyBridgeShadowProbeResponse(BaseModel):
    conversation_id: str
    client_event_id: str | None = None
    probe_id: str | None = None
    route: str
    message: str
    metadata_only: bool = True
    execution_enabled: bool = False
    blocked: bool = True
    reason: str | None = None
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    contract_only: bool = True
    legacy_builder_called: bool = False
    safety: dict[str, Any] = Field(default_factory=dict)
    bridge_probe: dict[str, Any] = Field(default_factory=dict)
    execution_locks: dict[str, Any] = Field(default_factory=dict)
    blocked_by_policy: list[str] = Field(default_factory=list)
    next_safe_action: str | None = None
    contract_schema_version: str | None = None
    legacy_target: str | None = None
    contract: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None

