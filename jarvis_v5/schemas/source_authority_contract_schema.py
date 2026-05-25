from __future__ import annotations

from pydantic import BaseModel, Field


class SourceAuthoritySafetyEnvelope(BaseModel):
    metadata_only: bool = True
    execution_enabled: bool = False
    document_read: bool = False
    ocr_enabled: bool = False
    rag_enabled: bool = False
    web_lookup_enabled: bool = False
    standards_ingestion_enabled: bool = False
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False


class SourceAuthorityUsagePolicy(BaseModel):
    can_inform_boq: bool = True
    can_claim_compliance: bool = False
    can_certify_compliance: bool = False
    requires_current_source: bool = True
    allowed_qs_advisory_use: list[str] = Field(default_factory=list)
    blocked_claims: list[str] = Field(default_factory=lambda: ["compliance confirmed", "certification confirmed"])


class SourceAuthorityCitationPlaceholder(BaseModel):
    citation_source_placeholder: bool = True
    source_reference_future: str | None = None
    source_revision_future: str | None = None


class SourceAuthorityHumanReviewRequirement(BaseModel):
    requires_human_review: bool = True
    review_reason: str = "Source authority contract only. Human review and current-source verification required."


class SourceAuthorityContractSpec(BaseModel):
    authority_key: str
    authority_level: str
    usage_policy: SourceAuthorityUsagePolicy = Field(default_factory=SourceAuthorityUsagePolicy)
    citation: SourceAuthorityCitationPlaceholder = Field(default_factory=SourceAuthorityCitationPlaceholder)
    human_review: SourceAuthorityHumanReviewRequirement = Field(default_factory=SourceAuthorityHumanReviewRequirement)
    safety: SourceAuthoritySafetyEnvelope = Field(default_factory=SourceAuthoritySafetyEnvelope)
    metadata_only: bool = True
    execution_enabled: bool = False


class SourceAuthorityContractMapResponse(BaseModel):
    version: str
    route: str = "source_authority_contract_map_metadata_only"
    authorities: list[SourceAuthorityContractSpec] = Field(default_factory=list)
    metadata_only: bool = True
    execution_enabled: bool = False
    document_read: bool = False
    ocr_enabled: bool = False
    rag_enabled: bool = False
    web_lookup_enabled: bool = False
    standards_ingestion_enabled: bool = False
    workbook_read: bool = False
    can_claim_compliance: bool = False
    can_certify_compliance: bool = False
