from __future__ import annotations

from pydantic import BaseModel, Field


class JobSafetyEnvelope(BaseModel):
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False
    metadata_only: bool = True
    execution_enabled: bool = False


class JobApprovalState(BaseModel):
    state: str = "requires_approval"
    approved_by: str | None = None
    approval_token: str | None = None
    approved_at: str | None = None
    expires_at: str | None = None


class JobProgressState(BaseModel):
    state: str = "draft"
    percent: int = 0
    message: str = "Contract only. No worker is connected."


class JobErrorRetryContract(BaseModel):
    error_code: str | None = None
    error_message_safe: str | None = None
    technical_detail_hidden: bool = True
    retry_allowed: bool = False
    retry_count: int = 0
    max_retries: int = 0
    rollback_action: str | None = None
    support_log_ref_future: str | None = None


class JobAuditEventContract(BaseModel):
    event_id: str
    job_id: str
    event_type: str
    actor: str = "system"
    timestamp: str | None = None
    source_contract_id: str | None = None
    safety_snapshot: JobSafetyEnvelope = Field(default_factory=JobSafetyEnvelope)


class JobContractSpec(BaseModel):
    job_id: str
    job_type: str
    source_contract_id: str
    source_tool_key: str
    conversation_id: str | None = None
    project_id: str | None = None
    approval: JobApprovalState = Field(default_factory=JobApprovalState)
    progress: JobProgressState = Field(default_factory=JobProgressState)
    safety: JobSafetyEnvelope = Field(default_factory=JobSafetyEnvelope)
    error_retry: JobErrorRetryContract = Field(default_factory=JobErrorRetryContract)
    metadata_only: bool = True
    execution_enabled: bool = False
