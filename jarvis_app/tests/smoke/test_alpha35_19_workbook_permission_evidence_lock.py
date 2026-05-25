from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.workbook_permission_contract_schema import (
    WorkbookPermissionContractMapResponse,
    WorkbookReadPermissionContract,
    WorkbookReadSafetyEnvelope,
)

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"
PROTECTED = [
    "jarvis_v5/tools/builder/adapter_dry_run.py",
    "jarvis_v5/tools/builder/engine_contract_adapter.py",
    "jarvis_v5/tools/builder/engine_boundary_audit.py",
    "jarvis_v5/tools/builder/engine_preflight.py",
    "jarvis_v5/tools/builder/legacy_engine_bridge.py",
    "jarvis_v5/tools/builder/preview_execution_policy.py",
    "jarvis_v5/tools/builder/safe_workbook_path_resolver.py",
    "jarvis_v5/tools/builder/setup_completeness.py",
    "jarvis_v5/tools/builder/workbook_read_policy_review.py",
    "jarvis_v5/tools/builder/workbook_read_preflight_contract.py",
]


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


def _registry_json_files() -> list[Path]:
    return sorted(REGISTRY.glob("*.json"))


def test_alpha35_19_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_workbook_permission_contract_still_blocks_probe_and_content_reads() -> None:
    safety = WorkbookReadSafetyEnvelope()
    assert safety.metadata_only is True
    assert safety.execution_enabled is False
    assert safety.workbook_read is False
    assert safety.workbook_content_read is False
    assert safety.sheet_name_probe_allowed is False
    assert safety.sheet_name_probe_requires_separate_approval is True
    assert safety.formula_read is False
    assert safety.cell_value_read is False

    contract = WorkbookReadPermissionContract(permission_request_id="perm_alpha35_19")
    assert contract.metadata_only is True
    assert contract.execution_enabled is False
    assert contract.approval.state == "requires_approval"
    assert contract.approval.approved_sheet_name_probe is False
    assert contract.approval.approved_content_read is False
    assert contract.sheet_scope.sheet_name_probe_allowed is False
    assert contract.range_scope.formula_read_allowed is False
    assert contract.range_scope.cell_value_read_allowed is False
    assert contract.content_read_permission_exists is False
    assert contract.workbook_content_read is False

    response = WorkbookPermissionContractMapResponse(version=APP_VERSION, contracts=[contract])
    assert response.workbook_read is False
    assert response.workbook_content_read is False
    assert response.sheet_name_probe_allowed is False
    assert response.formula_read is False
    assert response.cell_value_read is False


def test_registry_flags_do_not_enable_workbook_probe_or_content_read() -> None:
    bad_true_keys = {
        "execution_enabled",
        "workbook_read",
        "workbook_content_read",
        "formula_read",
        "cell_value_read",
        "sheet_name_probe_allowed",
        "engine_called",
        "excel_created",
        "legacy_builder_called",
        "tool_execution_called",
    }
    for path in _registry_json_files():
        data = json.loads(path.read_text())
        for item in _walk(data):
            for key in bad_true_keys:
                if key in item:
                    assert item[key] is not True, f"{path} has {key}=true in {item}"


def test_direct_workbook_content_request_still_safe_blocked() -> None:
    response = _client().post(
        "/api/chat",
        json={
            "conversation_id": "alpha3519_direct_workbook_read",
            "client_event_id": "alpha3519_direct_workbook_read",
            "text": "Open the workbook, list every sheet, read formulas, and read cell values.",
        },
    ).json()
    assert response["workbook_read"] is False
    assert response["engine_called"] is False
    assert response["excel_created"] is False
    assert response["legacy_builder_called"] is False


def test_protected_builder_boundary_files_exist_for_hash_lock() -> None:
    for rel in PROTECTED:
        path = ROOT / rel
        assert path.exists(), rel


def test_workbook_metadata_probe_readiness_docs_exist() -> None:
    docs = ROOT / "jarvis_v5" / "docs"
    for name in [
        "ALPHA_35_19_SCOPE.md",
        "WORKBOOK_PERMISSION_EVIDENCE_LOCK_ALPHA_35_19.md",
        "WORKBOOK_METADATA_PROBE_READINESS_REVIEW.md",
        "ROADMAP_AFTER_ALPHA_35_18.md",
    ]:
        assert (docs / name).exists(), name
