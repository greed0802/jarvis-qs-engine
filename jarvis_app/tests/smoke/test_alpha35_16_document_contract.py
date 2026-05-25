from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.document_contract_schema import DocumentContractMapResponse, DocumentContractSpec, DocumentSafetyEnvelope


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"


def _client() -> TestClient:
    return TestClient(app)


def _load_registry(name: str) -> dict:
    return json.loads((REGISTRY / name).read_text())


def test_alpha35_16_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_document_contract_schema_defaults_are_no_read_no_ocr() -> None:
    safety = DocumentSafetyEnvelope()
    assert safety.metadata_only is True
    assert safety.execution_enabled is False
    assert safety.document_read is False
    assert safety.ocr_enabled is False
    assert safety.rag_enabled is False
    assert safety.workbook_read is False
    assert safety.tool_execution_called is False

    spec = DocumentContractSpec(
        document_type_key="acoustic_report",
        display_name="Acoustic Report",
        source_authority_level="consultant_report",
    )
    assert spec.metadata_only is True
    assert spec.execution_enabled is False
    assert spec.human_review.required_human_review is True
    assert spec.citation.citation_source_placeholder is True
    assert spec.safety.document_read is False
    assert spec.safety.ocr_enabled is False
    assert spec.safety.rag_enabled is False

    response = DocumentContractMapResponse(version=APP_VERSION, contracts=[spec])
    assert response.document_read is False
    assert response.ocr_enabled is False
    assert response.rag_enabled is False
    assert response.workbook_read is False


def test_document_type_registry_entries_are_metadata_only() -> None:
    registry = _load_registry("document_type_registry.json")
    assert registry["metadata_only"] is True
    assert registry["execution_enabled"] is False
    assert registry["document_read"] is False
    assert registry["ocr_enabled"] is False
    assert registry["rag_enabled"] is False
    keys = {item["document_type_key"]: item for item in registry["document_types"]}
    expected = {
        "acoustic_report",
        "j1v3_jv3_energy_report",
        "bca_ncc_report",
        "fire_engineering_report",
        "access_report",
        "stormwater_report",
        "traffic_report",
        "geotech_report",
        "arborist_report",
        "da_consent_council_conditions",
        "specification",
        "addenda_rfi_log",
    }
    assert expected.issubset(keys)
    for item in keys.values():
        assert item["metadata_only"] is True
        assert item["execution_enabled"] is False
        assert item["document_read"] is False
        assert item["ocr_enabled"] is False
        assert item["rag_enabled"] is False
        assert item["workbook_read"] is False
        assert item["required_human_review"] is True
        assert item["citation_source_placeholder"] is True
        assert item["allowed_extraction_goals"]
        assert item["qs_scope_impact_fields"]
        assert item["boq_risk_fields"]
        assert item["rfi_candidate_fields"]


def test_source_authorities_do_not_claim_compliance() -> None:
    registry = _client().get("/api/registry/source-authorities").json()
    assert registry["metadata_only"] is True
    assert registry["execution_enabled"] is False
    keys = {item["authority_key"]: item for item in registry["authorities"]}
    for key in ["certifier_report", "fire_engineer_report", "council_condition", "rfi_response", "addendum"]:
        assert key in keys
        assert keys[key]["can_claim_compliance"] is False
        assert keys[key]["metadata_only"] is True
        assert keys[key]["execution_enabled"] is False


def test_document_reader_tool_and_ocr_capability_remain_disabled() -> None:
    tools = {item["tool_key"]: item for item in _client().get("/api/registry/tools").json()["tools"]}
    reader = tools["client_document_reader"]
    assert reader["metadata_only"] is True
    assert reader["execution_enabled"] is False
    assert reader["document_read"] is False
    assert reader["ocr_enabled"] is False
    assert reader["rag_enabled"] is False
    assert reader["human_review_required"] is True
    assert "document_read" in reader["blocked_in_alpha35_16"]
    assert "ocr" in reader["blocked_in_alpha35_16"]

    capabilities = {item["capability_key"]: item for item in _client().get("/api/registry/capabilities").json()["capabilities"]}
    for key in ["document_ocr", "classify_document_type_contract", "generate_document_rfi_candidates_contract"]:
        cap = capabilities[key]
        assert cap["metadata_only"] is True
        assert cap["execution_enabled"] is False
        assert cap["document_read"] is False
        assert cap["ocr_enabled"] is False
        assert cap["rag_enabled"] is False


def test_file_requirements_document_types_exist_metadata_only() -> None:
    requirements = {item["file_key"]: item for item in _client().get("/api/registry/file-requirements").json()["file_requirements"]}
    for key in ["bca_ncc_report", "stormwater_report", "traffic_report", "geotech_report", "arborist_report", "document_contract_future"]:
        item = requirements[key]
        assert item["metadata_only"] is True
        assert item["execution_enabled"] is False
        assert item["document_read"] is False
        assert item["ocr_enabled"] is False
        assert item["rag_enabled"] is False
