from __future__ import annotations

import json
from pathlib import Path
from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.tools.builder.workbook_metadata_probe_approval import evaluate_workbook_metadata_probe_approval

FORBIDDEN_EXACT_RAW_PATH_KEYS = {
    "saved_path",
    "absolute_path",
    "file_path",
    "local_path",
    "stored_path",
    "resolved_path",
    "raw_path",
    "attachment_path",
    "directory",
    "parent",
    "full_path",
    "path",
}


def _client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, cid: str, event: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    ).json()


def _alpha33_metadata_probe_contains_forbidden_exact_key(payload) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_EXACT_RAW_PATH_KEYS:
                return True
            if _alpha33_metadata_probe_contains_forbidden_exact_key(value):
                return True
    if isinstance(payload, list):
        return any(_alpha33_metadata_probe_contains_forbidden_exact_key(item) for item in payload)
    return False


def _alpha33_metadata_probe_ready_contract(client: TestClient, cid: str) -> tuple[dict, str]:
    assert _chat(client, cid, "start", "Build me a BOQ")["route"] == "new_builder_task_shell"
    with open("jarvis_v5/tests/fixtures/Test.xlsx", "rb") as fh:
        attach = client.post(
            "/api/attach",
            data={"conversation_id": cid, "client_event_id": "attach", "text": "Here"},
            files={"file": ("Test.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        ).json()
    assert attach["route"] == "attachment_bind"
    for event, text in [
        ("trade", "Use Wall Types"),
        ("func", "Use XGETWALLAREA"),
        ("unit", "Unit m2"),
        ("zone", "Zone 1: Old and New"),
        ("head", "Use Head 2 for Zone 1"),
        ("levels", "Levels GF to L3"),
    ]:
        assert _chat(client, cid, event, text)["route"] == "active_task_slot_edit"
    assert client.post("/api/builder/create-snapshot", json={"conversation_id": cid, "client_event_id": "snap"}).json()["route"] == "builder_snapshot_created"
    assert client.post("/api/builder/adapter-dry-run", json={"conversation_id": cid, "client_event_id": "adapter"}).json()["route"] == "builder_adapter_dry_run"
    contract = client.post("/api/builder/engine-contract", json={"conversation_id": cid, "client_event_id": "contract"}).json()
    assert contract["route"] == "builder_engine_contract_created"
    raw_saved_path = contract["contract"]["workbook_ref"]["saved_path"]
    assert raw_saved_path
    return contract, raw_saved_path


def _alpha33_assert_metadata_probe_safety(data: dict) -> None:
    assert data["metadata_only"] is True
    assert data["execution_enabled"] is False
    assert data["workbook_opened"] is False
    assert data["workbook_read"] is False
    assert data["workbook_parsed"] is False
    assert data["sheet_names_read"] is False
    assert data["cells_read"] is False
    assert data["formulas_read"] is False
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False
    assert data["safety"]["workbook_opened"] is False
    assert data["safety"]["workbook_read"] is False
    assert data["safety"]["workbook_parsed"] is False
    assert data["safety"]["sheet_names_read"] is False
    assert data["safety"]["cells_read"] is False
    assert data["safety"]["formulas_read"] is False
    assert data["preview_readiness_upgraded"] is False
    assert data["export_readiness_upgraded"] is False


def test_alpha33_version_metadata_probe_locks() -> None:
    version = _client().get("/api/version").json()
    assert version["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert version["scope"] == "workbook_read_policy_review_no_content_read"
    assert version["scope_metadata"]["workbook_metadata_probe_approval_contract"] is True
    assert version["scope_metadata"]["workbook_metadata_probe_approval_required_by_default"] is True
    assert version["scope_metadata"]["workbook_metadata_probe_metadata_only"] is True
    assert version["scope_metadata"]["workbook_sheet_names_enabled"] is True
    assert version["scope_metadata"]["workbook_parse_enabled"] is False
    assert version["execution_locks"]["workbook_read_enabled"] is False
    assert version["execution_locks"]["builder_engine_execution_enabled"] is False
    assert version["execution_locks"]["legacy_builder_callable"] is False
    assert version["execution_locks"]["excel_output_enabled"] is False


def test_alpha33_no_contract_blocks_metadata_probe() -> None:
    data = _client().post(
        "/api/builder/workbook-metadata-probe-approval",
        json={"conversation_id": "alpha33_no_contract", "client_event_id": "probe", "approval_granted": False},
    ).json()
    assert data["route"] == "builder_workbook_metadata_probe_approval"
    assert data["blocked"] is True
    assert data["approval_required"] is True
    assert data["approval_granted"] is False
    assert data["reason"] == "engine_contract_not_found"
    assert data["contract_found"] is False
    assert data["workbook_ref_found"] is False
    _alpha33_assert_metadata_probe_safety(data)
    assert _alpha33_metadata_probe_contains_forbidden_exact_key(data) is False


def test_alpha33_contract_without_workbook_ref_blocks() -> None:
    fake_contract = {"contract_id": "contract_fake", "conversation_id": "fake", "workbook_ref": {}}
    data = evaluate_workbook_metadata_probe_approval(
        conversation_id="alpha33_no_workbook_ref",
        client_event_id="direct",
        contract=fake_contract,
        approval_granted=True,
    )
    assert data["route"] == "builder_workbook_metadata_probe_approval"
    assert data["blocked"] is True
    assert data["reason"] == "workbook_ref_not_found"
    assert data["contract_found"] is True
    assert data["workbook_ref_found"] is False
    _alpha33_assert_metadata_probe_safety(data)
    assert _alpha33_metadata_probe_contains_forbidden_exact_key(data) is False


def test_alpha33_approval_required_by_default_for_alpha33_metadata_probe_ready_contract() -> None:
    client = _client()
    _contract, raw_saved_path = _alpha33_metadata_probe_ready_contract(client, "alpha33_approval_required")
    data = client.post(
        "/api/builder/workbook-metadata-probe-approval",
        json={"conversation_id": "alpha33_approval_required", "client_event_id": "probe", "approval_granted": False},
    ).json()
    assert data["route"] == "builder_workbook_metadata_probe_approval"
    assert data["blocked"] is True
    assert data["reason"] == "metadata_probe_approval_required"
    assert data["approval_required"] is True
    assert data["approval_granted"] is False
    assert data["contract_found"] is True
    assert data["workbook_ref_found"] is True
    assert "filename" in data["allowed_metadata_fields"]
    assert "read_sheet_names" in data["blocked_operations"]
    _alpha33_assert_metadata_probe_safety(data)
    assert data["raw_path_value_returned"] is False
    assert data["forbidden_path_key_returned"] is False
    assert _alpha33_metadata_probe_contains_forbidden_exact_key(data) is False
    assert raw_saved_path not in json.dumps(data, sort_keys=True)


def test_alpha33_approved_probe_returns_metadata_only() -> None:
    client = _client()
    _contract, raw_saved_path = _alpha33_metadata_probe_ready_contract(client, "alpha33_approved")
    data = client.post(
        "/api/builder/workbook-metadata-probe-approval",
        json={"conversation_id": "alpha33_approved", "client_event_id": "probe", "approval_granted": True},
    ).json()
    assert data["route"] == "builder_workbook_metadata_probe_approval"
    assert data["blocked"] is False
    assert data["reason"] == "metadata_probe_approved_metadata_only"
    assert data["approval_required"] is False
    assert data["approval_granted"] is True
    assert data["workbook_metadata"]["filename"] == "Test.xlsx"
    assert data["workbook_metadata"]["extension"] == ".xlsx"
    assert data["metadata_validation"]["metadata_probe_candidate_allowed"] is True
    _alpha33_assert_metadata_probe_safety(data)
    assert data["raw_path_value_returned"] is False
    assert data["forbidden_path_key_returned"] is False
    assert _alpha33_metadata_probe_contains_forbidden_exact_key(data) is False
    assert raw_saved_path not in json.dumps(data, sort_keys=True)


def test_alpha33_existing_preview_and_preflight_policies_unchanged() -> None:
    client = _client()
    _alpha33_metadata_probe_ready_contract(client, "alpha33_existing_policies")
    preview = client.post(
        "/api/builder/preview-execution-policy",
        json={"conversation_id": "alpha33_existing_policies", "client_event_id": "preview", "requested_action": "preview"},
    ).json()
    assert preview["route"] == "builder_preview_execution_policy"
    assert preview["workbook_read"] is False
    assert preview["engine_called"] is False
    assert preview["excel_created"] is False
    preflight = client.post(
        "/api/builder/workbook-read-preflight-dry-run",
        json={"conversation_id": "alpha33_existing_policies", "client_event_id": "preflight"},
    ).json()
    assert preflight["route"] == "builder_workbook_read_preflight_dry_run"
    assert preflight["workbook_read"] is False
    assert preflight["workbook_opened"] is False
    assert preflight["workbook_parsed"] is False


def test_alpha33_endpoint_owner_is_isolated() -> None:
    root = Path(__file__).resolve().parents[3]
    py_files = [p for p in (root / "jarvis_v5").rglob("*.py") if "__pycache__" not in p.parts]
    endpoint_refs = []
    logic_refs = []
    forbidden_import_refs = []
    for path in py_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root).as_posix()
        if "workbook-metadata-probe-approval" in text:
            endpoint_refs.append(rel)
        if "evaluate_workbook_metadata_probe_approval" in text:
            logic_refs.append(rel)
        if rel == "jarvis_v5/tools/builder/workbook_metadata_probe_approval.py":
            lowered = text.lower()
            for token in ["openpyxl", "pandas", "xlrd", "load_workbook", "path.open(", "open("]:
                if token in lowered:
                    forbidden_import_refs.append(token)
    assert "jarvis_v5/app.py" in endpoint_refs
    assert "jarvis_v5/tools/builder/workbook_metadata_probe_approval.py" in logic_refs
    runtime_logic_refs = [ref for ref in logic_refs if not ref.startswith("jarvis_v5/tests/")]
    assert runtime_logic_refs == [
        "jarvis_v5/app.py",
        "jarvis_v5/tools/builder/workbook_metadata_probe_approval.py",
    ]
    assert forbidden_import_refs == []
