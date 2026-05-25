from __future__ import annotations

import ast
import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.workbook_metadata_probe_contract_schema import (
    SheetNameOnlyProbeOutputContract,
    WorkbookMetadataProbeAllowedScope,
    WorkbookMetadataProbeApprovalRequirement,
    WorkbookMetadataProbeAuditRequirement,
    WorkbookMetadataProbeBlockedReadMatrix,
    WorkbookMetadataProbeBlockedResult,
    WorkbookMetadataProbeFileReferenceRequirement,
    WorkbookMetadataProbePlanResponse,
    WorkbookMetadataProbeRollbackBlockBehavior,
    WorkbookMetadataProbeSafetyEnvelope,
)

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"
DOCS = ROOT / "jarvis_v5" / "docs"
SCHEMA = ROOT / "jarvis_v5" / "schemas" / "workbook_metadata_probe_contract_schema.py"


def _client() -> TestClient:
    return TestClient(app)


def _walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_alpha36_1_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_workbook_metadata_probe_plan_schema_defaults_are_no_read() -> None:
    safety = WorkbookMetadataProbeSafetyEnvelope()
    assert safety.metadata_only is True
    assert safety.execution_enabled is False
    assert safety.workbook_read is False
    assert safety.workbook_content_read is False
    assert safety.sheet_name_probe_allowed is False
    assert safety.formula_read is False
    assert safety.cell_value_read is False
    assert safety.style_read is False

    allowed = WorkbookMetadataProbeAllowedScope()
    assert allowed.future_only is True
    assert allowed.workbook_opened is False
    assert allowed.sheet_name_probe_allowed is False
    assert allowed.safe_path_resolver_called is False

    blocked = WorkbookMetadataProbeBlockedReadMatrix()
    assert blocked.workbook_content_read is False
    assert blocked.formula_read is False
    assert blocked.cell_value_read is False
    assert blocked.style_read is False
    assert blocked.dimension_read is False

    approval = WorkbookMetadataProbeApprovalRequirement()
    assert approval.approval_required is True
    assert approval.approval_grants_runtime_permission is False
    assert approval.sheet_name_probe_allowed is False

    file_ref = WorkbookMetadataProbeFileReferenceRequirement()
    assert file_ref.file_opened is False
    assert file_ref.path_resolved is False
    assert file_ref.safe_path_resolver_called is False

    audit = WorkbookMetadataProbeAuditRequirement()
    assert audit.audit_schema_only is True
    assert audit.audit_event_written is False
    assert audit.safety_snapshot.workbook_read is False

    output = SheetNameOnlyProbeOutputContract()
    assert output.status == "future_only_not_enabled"
    assert output.sheet_names == []
    assert output.workbook_read is False
    assert output.style_read is False

    blocked_result = WorkbookMetadataProbeBlockedResult()
    assert blocked_result.status == "blocked"
    assert blocked_result.sheet_names == []
    assert blocked_result.sheet_name_probe_allowed is False
    assert blocked_result.workbook_read is False

    rollback = WorkbookMetadataProbeRollbackBlockBehavior()
    assert rollback.no_runtime_changes_to_rollback is True
    assert rollback.metadata_approval_still_blocks_runtime_probe is True

    response = WorkbookMetadataProbePlanResponse(version=APP_VERSION)
    assert response.workbook_read is False
    assert response.workbook_content_read is False
    assert response.sheet_name_probe_allowed is False
    assert response.formula_read is False
    assert response.cell_value_read is False
    assert response.style_read is False


def test_registry_metadata_probe_plan_keeps_all_read_flags_false() -> None:
    bad_true_keys = {
        "execution_enabled",
        "workbook_read",
        "workbook_content_read",
        "sheet_name_probe_allowed",
        "formula_read",
        "cell_value_read",
        "style_read",
        "engine_called",
        "excel_created",
        "legacy_builder_called",
        "tool_execution_called",
    }
    for path in sorted(REGISTRY.glob("*.json")):
        data = json.loads(path.read_text())
        for item in _walk(data):
            for key in bad_true_keys:
                if key in item:
                    assert item[key] is not True, f"{path} has {key}=true in {item}"


def test_execution_policy_and_capability_probe_plan_are_disabled() -> None:
    policies = json.loads((REGISTRY / "execution_policy_registry.json").read_text())["policies"]
    by_policy = {p["policy_key"]: p for p in policies}
    policy = by_policy["workbook_metadata_probe_plan"]
    assert policy["metadata_only"] is True
    assert policy["execution_enabled"] is False
    assert policy["workbook_read"] is False
    assert policy["sheet_name_probe_allowed"] is False
    assert policy["formula_read"] is False
    assert policy["cell_value_read"] is False
    assert policy["style_read"] is False

    capabilities = json.loads((REGISTRY / "capability_registry.json").read_text())["capabilities"]
    by_cap = {c["capability_key"]: c for c in capabilities}
    for key in [
        "workbook_metadata_probe_plan",
        "sheet_name_only_probe_contract",
        "workbook_metadata_probe_blocked_result_contract",
    ]:
        cap = by_cap[key]
        assert cap["metadata_only"] is True
        assert cap["execution_enabled"] is False
        assert cap["workbook_read"] is False
        assert cap["sheet_name_probe_allowed"] is False


def test_probe_plan_schema_does_not_import_workbook_read_libraries_or_resolver() -> None:
    tree = ast.parse(SCHEMA.read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    banned = {"openpyxl", "pandas", "xlrd", "pyxlsb", "jarvis_v5.tools.builder.safe_workbook_path_resolver"}
    assert not (set(imports) & banned)
    text = SCHEMA.read_text()
    assert "load_workbook" not in text
    assert "safe_workbook_path_resolver" not in text


def test_direct_probe_request_still_safe_blocked() -> None:
    event_id = f"alpha361_direct_probe_block_{uuid4().hex}"
    response = _client().post(
        "/api/chat",
        json={
            "conversation_id": event_id,
            "client_event_id": event_id,
            "text": "Read this workbook and list sheet names, formulas, and cell values.",
        },
    ).json()
    assert response["workbook_read"] is False
    assert response["engine_called"] is False
    assert response["excel_created"] is False
    assert response["legacy_builder_called"] is False


def test_alpha36_1_docs_exist() -> None:
    for name in [
        "ALPHA_36_1_SCOPE.md",
        "WORKBOOK_METADATA_PROBE_PLAN.md",
        "SHEET_NAME_ONLY_PROBE_CONTRACT.md",
        "WORKBOOK_METADATA_PROBE_BLOCKED_READ_MATRIX.md",
        "WORKBOOK_METADATA_PROBE_AUDIT_REQUIREMENT.md",
        "ROADMAP_AFTER_ALPHA_36_0.md",
    ]:
        assert (DOCS / name).exists(), name
