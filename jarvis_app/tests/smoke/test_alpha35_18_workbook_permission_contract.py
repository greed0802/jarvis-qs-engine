from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.workbook_permission_contract_schema import (
    WorkbookPermissionAuditEventContract,
    WorkbookPermissionContractMapResponse,
    WorkbookReadPermissionContract,
    WorkbookReadSafetyEnvelope,
)


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"


def _client() -> TestClient:
    return TestClient(app)


def _load_registry(name: str) -> dict:
    return json.loads((REGISTRY / name).read_text())


def test_alpha35_18_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_workbook_permission_schema_defaults_are_no_read() -> None:
    safety = WorkbookReadSafetyEnvelope()
    assert safety.metadata_only is True
    assert safety.execution_enabled is False
    assert safety.workbook_read is False
    assert safety.workbook_content_read is False
    assert safety.sheet_name_probe_allowed is False
    assert safety.sheet_name_probe_requires_separate_approval is True
    assert safety.formula_read is False
    assert safety.cell_value_read is False
    assert safety.engine_called is False
    assert safety.excel_created is False
    assert safety.legacy_builder_called is False
    assert safety.tool_execution_called is False

    contract = WorkbookReadPermissionContract(permission_request_id="perm_test", source_contract_id=None) if False else WorkbookReadPermissionContract(permission_request_id="perm_test")
    assert contract.metadata_only is True
    assert contract.execution_enabled is False
    assert contract.approval.state == "requires_approval"
    assert contract.approval.approved_content_read is False
    assert contract.approval.approved_sheet_name_probe is False
    assert contract.file_reference.file_opened is False
    assert contract.file_reference.path_resolved is False
    assert contract.sheet_scope.sheet_name_probe_allowed is False
    assert contract.range_scope.formula_read_allowed is False
    assert contract.range_scope.cell_value_read_allowed is False
    assert contract.content_read_permission_exists is False
    assert contract.workbook_content_read is False
    assert contract.formula_read is False
    assert contract.cell_value_read is False

    event = WorkbookPermissionAuditEventContract(audit_event_id="evt_test", permission_request_id="perm_test", event_type="read_blocked")
    assert event.safety_snapshot.workbook_read is False
    response = WorkbookPermissionContractMapResponse(version=APP_VERSION, contracts=[contract])
    assert response.workbook_read is False
    assert response.workbook_content_read is False
    assert response.sheet_name_probe_allowed is False
    assert response.formula_read is False
    assert response.cell_value_read is False


def test_execution_policy_workbook_permission_contract_is_disabled() -> None:
    policies = {item["policy_key"]: item for item in _client().get("/api/registry/execution-policies").json()["policies"]}
    policy = policies["workbook_read_permission_contract"]
    assert policy["metadata_only"] is True
    assert policy["execution_enabled"] is False
    assert policy["workbook_read"] is False
    assert policy["workbook_content_read"] is False
    assert policy["formula_read"] is False
    assert policy["cell_value_read"] is False
    assert policy["sheet_name_probe_allowed"] is False
    assert "open_workbook" in policy["blocked"]
    assert "read_cell_values" in policy["blocked"]


def test_workbook_permission_capabilities_are_metadata_only() -> None:
    capabilities = {item["capability_key"]: item for item in _client().get("/api/registry/capabilities").json()["capabilities"]}
    for key in [
        "workbook_read_permission_contract",
        "workbook_metadata_permission_contract",
        "workbook_content_read_permission_placeholder",
        "workbook_read_audit_contract",
    ]:
        cap = capabilities[key]
        assert cap["metadata_only"] is True
        assert cap["execution_enabled"] is False
        assert cap["workbook_read"] is False
        assert cap["workbook_content_read"] is False
        assert cap["formula_read"] is False
        assert cap["cell_value_read"] is False
        assert cap["sheet_name_probe_allowed"] is False
        assert cap["tool_execution_called"] is False


def test_future_workbook_tools_require_permission_but_cannot_read() -> None:
    tools = {item["tool_key"]: item for item in _client().get("/api/registry/tools").json()["tools"]}
    for key in ["builder", "formatter", "qa_checker", "omission_addition", "compare_boq", "bulkcheck_helper", "output_center"]:
        tool = tools[key]
        assert tool["execution_enabled"] is False
        assert tool["requires_workbook_permission_future"] is True
        assert tool["workbook_permission_contract_required"] is True
        assert tool["workbook_read_enabled"] is False
        assert tool["workbook_read"] is False
        assert tool["workbook_content_read"] is False
        assert tool["formula_read"] is False
        assert tool["cell_value_read"] is False
        assert tool["sheet_name_probe_allowed"] is False
        assert tool["tool_execution_called"] is False


def test_file_requirement_workbook_permission_placeholders_metadata_only() -> None:
    requirements = {item["file_key"]: item for item in _client().get("/api/registry/file-requirements").json()["file_requirements"]}
    for key in ["workbook_file_reference", "allowed_sheet_scope", "allowed_range_scope", "workbook_permission_request", "workbook_read_audit_log_future"]:
        item = requirements[key]
        assert item["metadata_only"] is True
        assert item["execution_enabled"] is False
        assert item["workbook_read"] is False
        assert item["workbook_content_read"] is False
        assert item["formula_read"] is False
        assert item["cell_value_read"] is False
        assert item["sheet_name_probe_allowed"] is False


def test_direct_workbook_read_still_safe_blocked() -> None:
    response = _client().post(
        "/api/chat",
        json={
            "conversation_id": "alpha3518_read_workbook",
            "client_event_id": "alpha3518_read_workbook",
            "text": "Open the workbook, list sheets, read formulas and all cell values",
        },
    ).json()
    assert response["workbook_read"] is False
    assert response["engine_called"] is False
    assert response["excel_created"] is False
    assert response["legacy_builder_called"] is False
