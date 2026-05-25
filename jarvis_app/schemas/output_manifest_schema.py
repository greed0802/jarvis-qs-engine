from __future__ import annotations

from pydantic import BaseModel, Field

from jarvis_v5.schemas.job_contract_schema import JobSafetyEnvelope


class DownloadPolicyPlaceholder(BaseModel):
    download_enabled: bool = False
    download_route_future: str | None = None
    safe_path_required: bool = True
    expires_at_future: str | None = None
    requires_user_project_access: bool = True


class OutputRetentionPolicy(BaseModel):
    retention_class: str = "temporary_preview"
    retention_days_future: int | None = None
    cleanup_enabled: bool = False


class OutputManifestSpec(BaseModel):
    output_id: str
    job_id: str
    output_type: str
    source_tool_key: str
    filename_future: str | None = None
    file_path_future: str | None = None
    download_ref_future: str | None = None
    file_created: bool = False
    retention: OutputRetentionPolicy = Field(default_factory=OutputRetentionPolicy)
    download_policy: DownloadPolicyPlaceholder = Field(default_factory=DownloadPolicyPlaceholder)
    safety: JobSafetyEnvelope = Field(default_factory=JobSafetyEnvelope)
    audit_status: str = "contract_only"
    metadata_only: bool = True
    execution_enabled: bool = False
