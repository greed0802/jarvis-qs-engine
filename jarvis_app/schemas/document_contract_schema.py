from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentSafetyEnvelope(BaseModel):
    metadata_only: bool = True
    execution_enabled: bool = False
    document_read: bool = False
    ocr_enabled: bool = False
    rag_enabled: bool = False
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False


class DocumentCitationPlaceholder(BaseModel):
    citation_source_placeholder: bool = True
    citation_map_future: str | None = None
    source_page_refs_future: list[str] = Field(default_factory=list)


class DocumentHumanReviewRequirement(BaseModel):
    required_human_review: bool = True
    review_reason: str = "Document contract only. Human review required before relying on document-derived scope."


class DocumentExtractionGoal(BaseModel):
    goal_key: str
    description: str | None = None


class DocumentQSScopeImpactField(BaseModel):
    field_key: str
    description: str | None = None


class DocumentBOQRiskField(BaseModel):
    field_key: str
    description: str | None = None


class DocumentRFICandidateField(BaseModel):
    field_key: str
    description: str | None = None


class DocumentContractSpec(BaseModel):
    document_type_key: str
    display_name: str
    source_authority_level: str
    allowed_extraction_goals: list[str] = Field(default_factory=list)
    qs_scope_impact_fields: list[str] = Field(default_factory=list)
    boq_risk_fields: list[str] = Field(default_factory=list)
    rfi_candidate_fields: list[str] = Field(default_factory=list)
    human_review: DocumentHumanReviewRequirement = Field(default_factory=DocumentHumanReviewRequirement)
    citation: DocumentCitationPlaceholder = Field(default_factory=DocumentCitationPlaceholder)
    safety: DocumentSafetyEnvelope = Field(default_factory=DocumentSafetyEnvelope)
    metadata_only: bool = True
    execution_enabled: bool = False


class DocumentContractMapResponse(BaseModel):
    version: str
    route: str = "document_contract_map_metadata_only"
    contracts: list[DocumentContractSpec] = Field(default_factory=list)
    metadata_only: bool = True
    execution_enabled: bool = False
    document_read: bool = False
    ocr_enabled: bool = False
    rag_enabled: bool = False
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
