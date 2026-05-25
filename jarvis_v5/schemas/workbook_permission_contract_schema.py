from __future__ import annotations

from pydantic import BaseModel, Field


class WorkbookReadSafetyEnvelope(BaseModel):
    metadata_only: bool = True
    execution_enabled: bool = False
    workbook_read: bool = False
    workbook_content_read: bool = False
    sheet_name_probe_allowed: bool = False
    sheet_name_probe_requires_separate_approval: bool = True
    formula_read: bool = False
    cell_value_read: bool = False
    format_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False


class WorkbookPermissionApprovalState(BaseModel):
    state: str = "requires_approval"
    approved_metadata_only: bool = False
    approved_sheet_name_probe: bool = False
    approved_content_read: bool = False
    approved_by: str | None = None
    approved_at: str | None = None
    approval_token: str | None = None


class WorkbookFileReferenceContract(BaseModel):
    file_ref: str | None = None
    file_display_name: str | None = None
    file_hash_future: str | None = None
    upload_id_future: str | None = None
    safe_path_required: bool = True
    path_resolved: bool = False
    file_opened: bool = False


class WorkbookSheetScopeContract(BaseModel):
    sheet_scope_mode: str = "none"
    allowed_sheet_names_future: list[str] = Field(default_factory=list)
    allowed_sheet_patterns_future: list[str] = Field(default_factory=list)
    all_sheets_allowed: bool = False
    sheet_name_probe_allowed: bool = False
    sheet_name_probe_requires_separate_approval: bool = True


class WorkbookRangeScopeContract(BaseModel):
    range_scope_mode: str = "none"
    allowed_ranges_future: list[str] = Field(default_factory=list)
    max_rows_future: int | None = None
    max_columns_future: int | None = None
    formula_read_allowed: bool = False
    cell_value_read_allowed: bool = False
    format_read_allowed: bool = False


class WorkbookPermissionRevocationState(BaseModel):
    revoked: bool = False
    revoked_by: str | None = None
    revoked_at: str | None = None
    revocation_reason: str | None = None


class WorkbookPermissionExpiryState(BaseModel):
    expires_at_future: str | None = None
    expired: bool = False
    expiry_policy: str = "future_only_no_scheduler"


class WorkbookBlockedReadReason(BaseModel):
    reason_key: str
    description: str


class WorkbookReadPermissionContract(BaseModel):
    permission_request_id: str
    conversation_id: str | None = None
    project_id: str | None = None
    requested_by: str | None = None
    requested_at: str | None = None
    permission_scope: str = "metadata_only_permission_contract"
    approval: WorkbookPermissionApprovalState = Field(default_factory=WorkbookPermissionApprovalState)
    file_reference: WorkbookFileReferenceContract = Field(default_factory=WorkbookFileReferenceContract)
    sheet_scope: WorkbookSheetScopeContract = Field(default_factory=WorkbookSheetScopeContract)
    range_scope: WorkbookRangeScopeContract = Field(default_factory=WorkbookRangeScopeContract)
    revocation: WorkbookPermissionRevocationState = Field(default_factory=WorkbookPermissionRevocationState)
    expiry: WorkbookPermissionExpiryState = Field(default_factory=WorkbookPermissionExpiryState)
    safety: WorkbookReadSafetyEnvelope = Field(default_factory=WorkbookReadSafetyEnvelope)
    content_read_permission_exists: bool = False
    content_read_approved: bool = False
    workbook_content_read: bool = False
    formula_read: bool = False
    cell_value_read: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False


class WorkbookPermissionAuditEventContract(BaseModel):
    audit_event_id: str
    permission_request_id: str
    event_type: str
    actor: str = "system"
    timestamp: str | None = None
    blocked_reason: str | None = None
    source_route_future: str | None = None
    safety_snapshot: WorkbookReadSafetyEnvelope = Field(default_factory=WorkbookReadSafetyEnvelope)


class WorkbookPermissionContractMapResponse(BaseModel):
    version: str
    route: str = "workbook_permission_contract_metadata_only"
    contracts: list[WorkbookReadPermissionContract] = Field(default_factory=list)
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
