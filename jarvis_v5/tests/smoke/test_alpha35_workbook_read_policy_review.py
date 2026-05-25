from __future__ import annotations

import ast
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def _client() -> TestClient:
    return TestClient(app)


def _post_policy() -> dict:
    return _client().post(
        "/api/builder/workbook-read-policy-review",
        json={"conversation_id": "alpha35_3_policy_review", "client_event_id": "policy_001"},
    ).json()


def test_alpha35_3_version_policy_locks() -> None:
    version = _client().get("/api/version").json()
    assert version["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert version["scope"] == "workbook_read_policy_review_no_content_read"
    assert version["scope_metadata"]["workbook_read_policy_review_contract"] is True
    assert version["scope_metadata"]["workbook_sheet_name_probe_approval_contract"] is True
    assert version["scope_metadata"]["workbook_sheet_names_enabled"] is True
    assert version["scope_metadata"]["cell_read_enabled"] is False
    assert version["scope_metadata"]["formula_read_enabled"] is False
    assert version["scope_metadata"]["dimension_read_enabled"] is False
    assert version["scope_metadata"]["workbook_parse_enabled"] is False
    assert version["execution_locks"]["workbook_read_enabled"] is False
    assert version["execution_locks"]["builder_engine_execution_enabled"] is False
    assert version["execution_locks"]["legacy_builder_callable"] is False
    assert version["execution_locks"]["excel_output_enabled"] is False


def test_alpha35_3_policy_review_endpoint_policy_only() -> None:
    data = _post_policy()
    assert data["route"] == "builder_workbook_read_policy_review"
    assert data["policy_only"] is True
    assert data["current_access_tier"] == "sheet_name_probe_only"
    assert data["cell_read_enabled"] is False
    assert data["formula_read_enabled"] is False
    assert data["dimension_read_enabled"] is False
    assert data["workbook_parse_enabled"] is False
    assert data["workbook_opened"] is False
    assert data["workbook_read"] is False
    assert data["workbook_content_read"] is False
    assert data["workbook_parsed"] is False
    assert data["cells_read"] is False
    assert data["formulas_read"] is False
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False
    assert data["preview_readiness_upgraded"] is False
    assert data["export_readiness_upgraded"] is False
    assert data["readiness"]["next_gate"] == "future_structure_probe_policy_review"
    assert "structure_probe_policy" in data["required_future_approval_gates"]
    tiers = data["future_access_tiers"]
    assert tiers[0]["status"] == "available_alpha35"
    assert tiers[0]["workbook_opened"] is False
    assert tiers[0]["sheet_names_read"] is False
    assert tiers[0]["workbook_read"] is False
    assert tiers[0]["execution_enabled"] is False
    assert tiers[1]["status"] == "not_enabled"
    assert tiers[1]["workbook_opened"] is False
    assert tiers[1]["sheet_names_read"] is False
    assert tiers[1]["workbook_read"] is False
    assert tiers[1]["execution_enabled"] is False


def test_alpha35_3_alpha33_and_alpha34_endpoints_unchanged() -> None:
    client = _client()
    metadata = client.post(
        "/api/builder/workbook-metadata-probe-approval",
        json={"conversation_id": "alpha35_3_alpha33_guard", "client_event_id": "probe", "approval_granted": False},
    ).json()
    assert metadata["route"] == "builder_workbook_metadata_probe_approval"
    assert metadata["blocked"] is True
    assert metadata["reason"] == "engine_contract_not_found"
    assert metadata["workbook_opened"] is False
    assert metadata["sheet_names_read"] is False
    sheet = client.post(
        "/api/builder/workbook-sheet-name-probe-approval",
        json={"conversation_id": "alpha35_3_alpha34_guard", "client_event_id": "probe", "approval_granted": False},
    ).json()
    assert sheet["route"] == "builder_workbook_sheet_name_probe_approval"
    assert sheet["blocked"] is True
    assert sheet["reason"] == "engine_contract_not_found"
    assert sheet["workbook_opened"] is False
    assert sheet["sheet_names_read"] is False


def test_alpha35_3_policy_owner_has_no_workbook_access_imports() -> None:
    text = Path("jarvis_v5/tools/builder/workbook_read_policy_review.py").read_text(encoding="utf-8")
    lowered = text.lower()
    for token in ["openpyxl", "load_workbook", "pandas", "xlrd", "path.open(", "open("]:
        assert token not in lowered


def test_alpha35_3_openpyxl_owner_remains_sheet_name_module_only() -> None:
    root = Path(__file__).resolve().parents[3]
    py_files = [p for p in (root / "jarvis_v5").rglob("*.py") if "__pycache__" not in p.parts]
    import_refs = []
    load_workbook_call_refs = []
    forbidden_iteration_refs = []
    for path in py_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root).as_posix()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                if any(alias.name == "openpyxl" or alias.name.startswith("openpyxl.") for alias in node.names):
                    import_refs.append(rel)
            if isinstance(node, ast.ImportFrom):
                if node.module == "openpyxl" or (node.module or "").startswith("openpyxl."):
                    import_refs.append(rel)
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "load_workbook":
                    load_workbook_call_refs.append(rel)
                if isinstance(func, ast.Attribute) and func.attr == "load_workbook":
                    load_workbook_call_refs.append(rel)
        if rel == "jarvis_v5/tools/builder/workbook_sheet_name_probe_approval.py":
            lowered = text.lower()
            for token in [".rows", "iter_rows", ".columns", "calculate_dimension", ".value", ".save("]:
                if token in lowered:
                    forbidden_iteration_refs.append(token)
    assert sorted(set(import_refs)) == ["jarvis_v5/tools/builder/workbook_sheet_name_probe_approval.py"]
    assert sorted(set(load_workbook_call_refs)) == ["jarvis_v5/tools/builder/workbook_sheet_name_probe_approval.py"]
    assert forbidden_iteration_refs == []


def test_alpha35_3_endpoint_owner_is_isolated() -> None:
    root = Path(__file__).resolve().parents[3]
    py_files = [p for p in (root / "jarvis_v5").rglob("*.py") if "__pycache__" not in p.parts]
    endpoint_refs = []
    logic_refs = []
    for path in py_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root).as_posix()
        if "workbook-read-policy-review" in text:
            endpoint_refs.append(rel)
        if "evaluate_workbook_read_policy_review" in text:
            logic_refs.append(rel)
    assert "jarvis_v5/app.py" in endpoint_refs
    assert "jarvis_v5/qa_runner/test_executor.py" in endpoint_refs
    assert "jarvis_v5/tools/builder/workbook_read_policy_review.py" in logic_refs
    assert "jarvis_v5/app.py" in logic_refs
    runtime_logic_refs = [p for p in logic_refs if not p.startswith("jarvis_v5/tests/")]
    assert runtime_logic_refs == [
        "jarvis_v5/app.py",
        "jarvis_v5/router/main_router.py",
        "jarvis_v5/tools/builder/workbook_read_policy_review.py",
    ]
