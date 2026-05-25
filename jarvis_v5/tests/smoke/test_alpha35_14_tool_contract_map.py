from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.tool_contract_schema import ToolContractMapResponse, ToolContractSpec


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"

FUTURE_TOOL_KEYS = [
    "formatter",
    "qa_checker",
    "omission_addition",
    "bulkcheck_helper",
    "compare_boq",
    "description_helper",
    "client_document_reader",
    "standards_knowledge_base",
    "output_center",
]

CAPABILITY_KEYS = [
    "format_workbook",
    "qa_check_boq_quantities",
    "build_omission_addition_delta",
    "bulkcheck_unit_collation",
    "compare_boq_versions",
    "write_boq_descriptions",
    "extract_qs_scope_from_documents",
    "standards_reference_advisory",
    "manage_tool_outputs",
]


def _client() -> TestClient:
    return TestClient(app)


def _load_registry(name: str) -> dict:
    return json.loads((REGISTRY / name).read_text())


def test_alpha35_14_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_future_tool_contracts_exist_and_are_disabled() -> None:
    tools = {item["tool_key"]: item for item in _load_registry("tool_registry.json")["tools"]}
    for key in FUTURE_TOOL_KEYS:
        assert key in tools
        tool = tools[key]
        assert tool["metadata_only"] is True
        assert tool["execution_enabled"] is False
        assert tool["workbook_read_required"] is False
        assert tool["requires_approval_before_execution"] is True
        assert tool["contract_status"] == "planned_contract_only"
        assert tool["input_contract_fields"]
        assert tool["output_contract_fields"]
        assert tool["required_file_keys"]
        assert tool["safety_policy"]["workbook_read"] is False
        assert tool["safety_policy"]["engine_called"] is False
        assert tool["safety_policy"]["excel_created"] is False
        assert tool["safety_policy"]["legacy_builder_called"] is False
        assert tool["safety_policy"]["tool_execution_called"] is False


def test_capability_contracts_exist_and_map_to_tools() -> None:
    capabilities = {item["capability_key"]: item for item in _load_registry("capability_registry.json")["capabilities"]}
    for key in CAPABILITY_KEYS:
        assert key in capabilities
        cap = capabilities[key]
        assert cap["metadata_only"] is True
        assert cap["execution_enabled"] is False
        assert cap["contract_status"] == "planned_contract_only"
        assert cap["workbook_read_required"] is False
        assert cap["safe_first_mode"] == "contract_advisory_only"
        assert cap["possible_tools"]


def test_tool_contract_schema_defaults_are_no_execution() -> None:
    spec = ToolContractSpec(
        tool_key="formatter",
        capability_key="format_workbook",
        input_contract="formatter_input_contract_v1",
        output_contract="formatted_workbook_manifest_v1",
        approval_gate="approve_formatter_preflight",
        route_owner="future_formatter_contract_advisor",
    )
    assert spec.metadata_only is True
    assert spec.execution_enabled is False
    assert spec.workbook_read_required is False
    assert spec.safety_policy.workbook_read is False
    assert spec.safety_policy.engine_called is False
    assert spec.safety_policy.excel_created is False
    assert spec.safety_policy.legacy_builder_called is False
    assert spec.safety_policy.tool_execution_called is False

    response = ToolContractMapResponse(version=APP_VERSION, contracts=[spec])
    assert response.metadata_only is True
    assert response.execution_enabled is False
    assert response.workbook_read is False
    assert response.engine_called is False
    assert response.excel_created is False
    assert response.legacy_builder_called is False
    assert response.tool_execution_called is False


def test_registry_endpoints_remain_metadata_only() -> None:
    client = _client()
    for endpoint, list_key in [
        ("/api/registry/tools", "tools"),
        ("/api/registry/capabilities", "capabilities"),
        ("/api/registry/execution-policies", "policies"),
        ("/api/registry/file-requirements", "file_requirements"),
    ]:
        payload = client.get(endpoint).json()
        assert payload["metadata_only"] is True
        assert payload["execution_enabled"] is False
        assert payload[list_key]


def test_future_tool_requests_remain_metadata_only_no_execution() -> None:
    client = _client()
    for text in [
        "Run Formatter on the Builder output",
        "Run QA Checker now",
        "Run O&A on this workbook",
        "Run Document Reader on this report",
    ]:
        payload = client.post(
            "/api/chat",
            json={
                "conversation_id": f"alpha3514_{abs(hash(text))}",
                "client_event_id": f"alpha3514_{abs(hash(text))}",
                "text": text,
            },
        ).json()
        assert payload["route"] == "registry_advisory_metadata_only"
        assert payload["metadata_only"] is True
        assert payload["execution_enabled"] is False
        assert payload["workbook_read"] is False
        assert payload["engine_called"] is False
        assert payload["excel_created"] is False
        assert payload["legacy_builder_called"] is False
        advisor = payload["requirement_advisor"]
        assert advisor["future_tool_requested"] is True
        assert advisor["execution_requested"] is True
        assert advisor["execution_blocked"] is True
        assert advisor["blocked_reason"] == "future_tool_execution_disabled"
        assert advisor["tool_execution_called"] is False
