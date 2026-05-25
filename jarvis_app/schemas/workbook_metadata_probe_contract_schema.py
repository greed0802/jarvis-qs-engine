from __future__ import annotations

from pydantic import BaseModel, Field


class WorkbookMetadataProbeSafetyEnvelope(BaseModel):
    metadata_only: bool = True
    execution_enabled: bool = False
    workbook_read: bool = False
    workbook_content_read: bool = False
    sheet_name_probe_allowed: bool = False
    formula_read: bool = False
    cell_value_read: bool = False
    style_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False


class WorkbookMetadataProbeAllowedScope(BaseModel):
    probe_type: str = "sheet_name_only_future"
    future_only: bool = True
    file_exists_check_allowed: bool = False
    safe_path_review_required: bool = True
    safe_path_resolver_called: bool = False
    workbook_opened: bool = False
    sheet_name_probe_allowed: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: WorkbookMetadataProbeSafetyEnvelope = Field(default_factory=WorkbookMetadataProbeSafetyEnvelope)


class WorkbookMetadataProbeBlockedReadMatrix(BaseModel):
    workbook_content_read: bool = False
    formula_read: bool = False
    cell_value_read: bool = False
    style_read: bool = False
    dimension_read: bool = False
    range_read: bool = False
    table_read: bool = False
    defined_name_read: bool = False
    external_link_read: bool = False
    hidden_sheet_content_read: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: WorkbookMetadataProbeSafetyEnvelope = Field(default_factory=WorkbookMetadataProbeSafetyEnvelope)


class WorkbookMetadataProbeApprovalRequirement(BaseModel):
    approval_required: bool = True
    approval_type: str = "sheet_name_probe_approval_future"
    approval_grants_runtime_permission: bool = False
    approval_does_not_grant_content_read: bool = True
    sheet_name_probe_allowed: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: WorkbookMetadataProbeSafetyEnvelope = Field(default_factory=WorkbookMetadataProbeSafetyEnvelope)


class WorkbookMetadataProbeFileReferenceRequirement(BaseModel):
    file_ref: str | None = None
    file_display_name: str | None = None
    upload_id_future: str | None = None
    safe_path_review_required: bool = True
    safe_path_resolved: bool = False
    safe_path_resolver_called: bool = False
    path_resolved: bool = False
    file_opened: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: WorkbookMetadataProbeSafetyEnvelope = Field(default_factory=WorkbookMetadataProbeSafetyEnvelope)


class WorkbookMetadataProbeAuditRequirement(BaseModel):
    event_type: str = "sheet_name_probe_future"
    required_fields: list[str] = Field(
        default_factory=lambda: [
            "event_id",
            "file_ref",
            "approval_snapshot",
            "permission_snapshot",
            "safety_snapshot",
            "blocked_reason",
            "state_before",
            "state_after",
            "timestamp_future",
        ]
    )
    audit_schema_only: bool = True
    audit_event_written: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety_snapshot: WorkbookMetadataProbeSafetyEnvelope = Field(default_factory=WorkbookMetadataProbeSafetyEnvelope)


class SheetNameOnlyProbeOutputContract(BaseModel):
    status: str = "future_only_not_enabled"
    probe_type: str = "sheet_name_only"
    sheet_names: list[str] = Field(default_factory=list)
    sheet_count: int | None = None
    workbook_read: bool = False
    workbook_content_read: bool = False
    formula_read: bool = False
    cell_value_read: bool = False
    style_read: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: WorkbookMetadataProbeSafetyEnvelope = Field(default_factory=WorkbookMetadataProbeSafetyEnvelope)


class WorkbookMetadataProbeBlockedResult(BaseModel):
    status: str = "blocked"
    blocked_reason: str = "sheet_name_probe_not_enabled"
    required_next_step: str = "separate approval and future implementation required"
    sheet_names: list[str] = Field(default_factory=list)
    workbook_read: bool = False
    workbook_content_read: bool = False
    sheet_name_probe_allowed: bool = False
    formula_read: bool = False
    cell_value_read: bool = False
    style_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False


class WorkbookMetadataProbeRollbackBlockBehavior(BaseModel):
    no_runtime_changes_to_rollback: bool = True
    rollback_is_package_replacement_only: bool = True
    no_approval_blocks_probe: bool = True
    metadata_approval_still_blocks_runtime_probe: bool = True
    file_ref_missing_blocks_probe: bool = True
    safe_path_not_reviewed_blocks_probe: bool = True
    content_formula_cell_style_requests_blocked: bool = True
    metadata_only: bool = True
    execution_enabled: bool = False
    safety: WorkbookMetadataProbeSafetyEnvelope = Field(default_factory=WorkbookMetadataProbeSafetyEnvelope)


class WorkbookMetadataProbePlanResponse(BaseModel):
    version: str
    route: str = "workbook_metadata_probe_plan_metadata_only"
    allowed_scope: WorkbookMetadataProbeAllowedScope = Field(default_factory=WorkbookMetadataProbeAllowedScope)
    blocked_read_matrix: WorkbookMetadataProbeBlockedReadMatrix = Field(default_factory=WorkbookMetadataProbeBlockedReadMatrix)
    approval_requirement: WorkbookMetadataProbeApprovalRequirement = Field(default_factory=WorkbookMetadataProbeApprovalRequirement)
    file_reference_requirement: WorkbookMetadataProbeFileReferenceRequirement = Field(default_factory=WorkbookMetadataProbeFileReferenceRequirement)
    audit_requirement: WorkbookMetadataProbeAuditRequirement = Field(default_factory=WorkbookMetadataProbeAuditRequirement)
    output_contract: SheetNameOnlyProbeOutputContract = Field(default_factory=SheetNameOnlyProbeOutputContract)
    blocked_result: WorkbookMetadataProbeBlockedResult = Field(default_factory=WorkbookMetadataProbeBlockedResult)
    rollback_block_behavior: WorkbookMetadataProbeRollbackBlockBehavior = Field(default_factory=WorkbookMetadataProbeRollbackBlockBehavior)
    metadata_only: bool = True
    execution_enabled: bool = False
    workbook_read: bool = False
    workbook_content_read: bool = False
    sheet_name_probe_allowed: bool = False
    formula_read: bool = False
    cell_value_read: bool = False
    style_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False
