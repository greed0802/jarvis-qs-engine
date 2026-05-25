from __future__ import annotations

import json
from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION

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


def _alpha29_resolver_client() -> TestClient:
    return TestClient(app)


def _alpha29_resolver_chat(client: TestClient, cid: str, event: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    ).json()


def _alpha29_contains_forbidden_exact_key(payload) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_EXACT_RAW_PATH_KEYS:
                return True
            if _alpha29_contains_forbidden_exact_key(value):
                return True
    if isinstance(payload, list):
        return any(_alpha29_contains_forbidden_exact_key(item) for item in payload)
    return False


def _alpha29_ready_contract(client: TestClient, cid: str) -> tuple[dict, str]:
    assert _alpha29_resolver_chat(client, cid, "start", "Build me a BOQ")["route"] == "new_builder_task_shell"
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
        assert _alpha29_resolver_chat(client, cid, event, text)["route"] == "active_task_slot_edit"
    assert client.post("/api/builder/create-snapshot", json={"conversation_id": cid, "client_event_id": "snap"}).json()["route"] == "builder_snapshot_created"
    assert client.post("/api/builder/adapter-dry-run", json={"conversation_id": cid, "client_event_id": "adapter"}).json()["route"] == "builder_adapter_dry_run"
    contract = client.post("/api/builder/engine-contract", json={"conversation_id": cid, "client_event_id": "contract"}).json()
    assert contract["route"] == "builder_engine_contract_created"
    saved_path = contract["contract"]["workbook_ref"]["saved_path"]
    assert saved_path
    return contract, saved_path


def test_alpha29_version_safe_workbook_path_resolver_metadata() -> None:
    client = _alpha29_resolver_client()
    version = client.get("/api/version").json()
    assert version["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert version["scope"] == "workbook_read_policy_review_no_content_read"
    assert version["scope_metadata"]["safe_workbook_path_resolver_dry_run"] is True
    assert version["scope_metadata"]["workbook_path_resolution_enabled"] is False
    assert version["scope_metadata"]["workbook_filesystem_check_enabled"] is False
    assert version["scope_metadata"]["workbook_open_enabled"] is False
    assert version["execution_locks"]["workbook_read_enabled"] is False
    assert version["execution_locks"]["builder_engine_execution_enabled"] is False
    assert version["execution_locks"]["legacy_builder_callable"] is False
    assert version["execution_locks"]["excel_output_enabled"] is False


def test_alpha29_no_contract_blocks_without_workbook_access() -> None:
    client = _alpha29_resolver_client()
    data = client.post(
        "/api/builder/safe-workbook-path-resolver-dry-run",
        json={"conversation_id": "smoke_alpha29_no_contract", "client_event_id": "resolver_no_contract"},
    ).json()
    assert data["route"] == "builder_safe_workbook_path_resolver_dry_run"
    assert data["metadata_only"] is True
    assert data["execution_enabled"] is False
    assert data["blocked"] is True
    assert data["reason"] == "engine_contract_not_found"
    assert data["contract_found"] is False
    assert data["workbook_ref_found"] is False
    assert data["workbook_ref_summary"]["found"] is False
    assert data["path_resolved"] is False
    assert data["filesystem_checked"] is False
    assert data["workbook_filesystem_checked"] is False
    assert data["workbook_opened"] is False
    assert data["workbook_read"] is False
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False
    assert data["raw_path_value_returned"] is False
    assert data["forbidden_path_key_returned"] is False
    assert _alpha29_contains_forbidden_exact_key(data) is False


def test_alpha29_ready_contract_summarizes_workbook_ref_without_raw_path() -> None:
    client = _alpha29_resolver_client()
    _contract, raw_saved_path = _alpha29_ready_contract(client, "smoke_alpha29_contract")
    data = client.post(
        "/api/builder/safe-workbook-path-resolver-dry-run",
        json={"conversation_id": "smoke_alpha29_contract", "client_event_id": "resolver_contract"},
    ).json()
    assert data["route"] == "builder_safe_workbook_path_resolver_dry_run"
    assert data["reason"] == "safe_workbook_path_resolver_dry_run_only"
    assert data["contract_found"] is True
    assert data["workbook_ref_found"] is True
    assert data["workbook_ref_summary"]["filename"] == "Test.xlsx"
    assert data["workbook_ref_summary"]["workbook_id"]
    assert data["workbook_ref_summary"]["attachment_id"]
    assert data["workbook_ref_summary"]["source"] == "upload"
    assert data["raw_saved_path_present"] is True
    assert data["path_like_metadata_present"] is True
    assert data["jarvis_metadata_store_read"] is True
    assert data["filesystem_check_required_later"] is True
    assert data["would_require_attachment_root_check_later"] is True
    assert data["path_resolved"] is False
    assert data["filesystem_checked"] is False
    assert data["workbook_filesystem_checked"] is False
    assert data["workbook_opened"] is False
    assert data["workbook_read"] is False
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False
    assert data["raw_path_value_returned"] is False
    assert data["forbidden_path_key_returned"] is False
    assert data["safety"]["raw_path_value_returned"] is False
    assert data["safety"]["forbidden_path_key_returned"] is False
    assert _alpha29_contains_forbidden_exact_key(data) is False
    assert raw_saved_path not in json.dumps(data, sort_keys=True)


def test_alpha29_resolver_endpoint_owner_is_isolated() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    py_files = [p for p in (root / "jarvis_v5").rglob("*.py") if "__pycache__" not in p.parts]
    endpoint_refs = []
    logic_refs = []
    for path in py_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root).as_posix()
        if "safe-workbook-path-resolver-dry-run" in text:
            endpoint_refs.append(rel)
        if "evaluate_safe_workbook_path_resolver_dry_run" in text:
            logic_refs.append(rel)
    assert "jarvis_v5/app.py" in endpoint_refs
    assert "jarvis_v5/tools/builder/safe_workbook_path_resolver.py" in logic_refs
    runtime_logic_refs = [ref for ref in logic_refs if not ref.startswith("jarvis_v5/tests/")]
    assert "jarvis_v5/tools/builder/safe_workbook_path_resolver.py" in runtime_logic_refs
    assert "jarvis_v5/app.py" in runtime_logic_refs
    assert set(runtime_logic_refs).issubset({
        "jarvis_v5/app.py",
        "jarvis_v5/tools/builder/safe_workbook_path_resolver.py",
        "jarvis_v5/tools/builder/workbook_read_preflight_contract.py",
    })
