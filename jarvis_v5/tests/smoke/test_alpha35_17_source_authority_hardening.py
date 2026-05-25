from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.source_authority_contract_schema import (
    SourceAuthorityContractMapResponse,
    SourceAuthorityContractSpec,
    SourceAuthoritySafetyEnvelope,
)


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"


def _client() -> TestClient:
    return TestClient(app)


def _load_registry(name: str) -> dict:
    return json.loads((REGISTRY / name).read_text())


def test_alpha35_17_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_source_authority_schema_defaults_are_safe() -> None:
    safety = SourceAuthoritySafetyEnvelope()
    assert safety.metadata_only is True
    assert safety.execution_enabled is False
    assert safety.document_read is False
    assert safety.ocr_enabled is False
    assert safety.rag_enabled is False
    assert safety.web_lookup_enabled is False
    assert safety.standards_ingestion_enabled is False
    assert safety.workbook_read is False
    assert safety.tool_execution_called is False

    spec = SourceAuthorityContractSpec(authority_key="ai_inference", authority_level="lowest_authority")
    assert spec.metadata_only is True
    assert spec.execution_enabled is False
    assert spec.usage_policy.can_claim_compliance is False
    assert spec.usage_policy.can_certify_compliance is False
    assert spec.human_review.requires_human_review is True
    assert spec.citation.citation_source_placeholder is True

    response = SourceAuthorityContractMapResponse(version=APP_VERSION, authorities=[spec])
    assert response.can_claim_compliance is False
    assert response.can_certify_compliance is False
    assert response.document_read is False
    assert response.rag_enabled is False


def test_source_authority_registry_is_metadata_only_no_compliance_claim() -> None:
    registry = _client().get("/api/registry/source-authorities").json()
    assert registry["metadata_only"] is True
    assert registry["execution_enabled"] is False
    required = {
        "statutory_code",
        "professional_standard",
        "client_standard",
        "consultant_report",
        "specification",
        "drawing_note",
        "council_condition",
        "addendum",
        "rfi_response",
        "user_assumption",
        "ai_inference",
    }
    authorities = {item["authority_key"]: item for item in registry["authorities"]}
    assert required.issubset(authorities)
    for item in authorities.values():
        assert item["metadata_only"] is True
        assert item["execution_enabled"] is False
        assert item["can_claim_compliance"] is False
        assert item["can_certify_compliance"] is False
        assert item["requires_human_review"] is True
        assert item["citation_source_placeholder"] is True
        assert item["document_read"] is False
        assert item["ocr_enabled"] is False
        assert item["rag_enabled"] is False
        assert item["web_lookup_enabled"] is False
        assert item["standards_ingestion_enabled"] is False
        assert item["workbook_read"] is False


def test_low_authority_user_assumption_and_ai_inference_are_not_project_facts() -> None:
    authorities = {item["authority_key"]: item for item in _client().get("/api/registry/source-authorities").json()["authorities"]}
    assumption = authorities["user_assumption"]
    inference = authorities["ai_inference"]
    assert assumption["must_be_marked_as_assumption"] is True
    assert assumption["can_certify_compliance"] is False
    assert "confirmed by project documents" in assumption["blocked_claims"]
    assert inference["must_be_marked_as_inference"] is True
    assert inference["authority_level"] == "lowest_authority_model_inference"
    assert inference["can_claim_compliance"] is False
    assert "project requirement" in inference["blocked_claims"]


def test_document_types_reference_non_compliance_authorities() -> None:
    registry = _load_registry("document_type_registry.json")
    for item in registry["document_types"]:
        assert item["metadata_only"] is True
        assert item["execution_enabled"] is False
        assert item["can_inform_boq"] is True
        assert item["can_claim_compliance"] is False
        assert item["can_certify_compliance"] is False
        assert item["requires_current_source"] is True
        assert item["requires_human_review"] is True
        assert item["authority_contract_required"] is True
        assert item["document_read"] is False
        assert item["ocr_enabled"] is False
        assert item["rag_enabled"] is False


def test_standards_and_document_capabilities_remain_disabled() -> None:
    capabilities = {item["capability_key"]: item for item in _client().get("/api/registry/capabilities").json()["capabilities"]}
    for key in ["check_standards", "standards_reference_advisory", "document_ocr", "classify_source_authority_contract", "compliance_claim_blocking_contract"]:
        cap = capabilities[key]
        assert cap["metadata_only"] is True
        assert cap["execution_enabled"] is False
        assert cap["document_read"] is False
        assert cap["ocr_enabled"] is False
        assert cap["rag_enabled"] is False
        assert cap["web_lookup_enabled"] is False
        assert cap["standards_ingestion_enabled"] is False
        assert cap["can_claim_compliance"] is False
        assert cap["can_certify_compliance"] is False


def test_standards_and_document_tools_remain_disabled() -> None:
    tools = {item["tool_key"]: item for item in _client().get("/api/registry/tools").json()["tools"]}
    for key in ["standards_knowledge_base", "client_document_reader"]:
        tool = tools[key]
        assert tool["metadata_only"] is True
        assert tool["execution_enabled"] is False
        assert tool["document_read"] is False
        assert tool["ocr_enabled"] is False
        assert tool["rag_enabled"] is False
        assert tool["web_lookup_enabled"] is False
        assert tool["standards_ingestion_enabled"] is False
        assert tool["can_claim_compliance"] is False
        assert tool["can_certify_compliance"] is False
        assert "compliance_certification" in tool["blocked_in_alpha35_17"]
