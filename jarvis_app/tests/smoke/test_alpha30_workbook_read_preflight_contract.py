from __future__ import annotations

import json
from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.tools.builder.workbook_read_preflight_contract import evaluate_workbook_read_preflight_dry_run

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


def _alpha30_client() -> TestClient:
    return TestClient(app)


def _alpha30_chat(client: TestClient, cid: str, event: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    ).json()


def _alpha30_contains_forbidden_exact_key(payload) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_EXACT_RAW_PATH_KEYS:
                return True
            if _alpha30_contains_forbidden_exact_key(value):
                return True
    if isinstance(payload, list):
        return any(_alpha30_contains_forbidden_exact_key(item) for item in payload)
    return False


def _alpha30_ready_contract(client: TestClient, cid: str) -> tuple[dict, str]:
    assert _alpha30_chat(client, cid, "start", "Build me a BOQ")["route"] == "new_builder_task_shell"
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
        assert _alpha30_chat(client, cid, event, text)["route"] == "active_task_slot_edit"
    assert client.post("/api/builder/create-snapshot", json={"conversation_id": cid, "client_event_id": "snap"}).json()["route"] == "builder_snapshot_created"
    assert client.post("/api/builder/adapter-dry-run", json={"conversation_id": cid, "client_event_id": "adapter"}).json()["route"] == "builder_adapter_dry_run"
    contract = client.post("/api/builder/engine-contract", json={"conversation_id": cid, "client_event_id": "contract"}).json()
    assert contract["route"] == "builder_engine_contract_created"
    raw_saved_path = contract["contract"]["workbook_ref"]["saved_path"]
    assert raw_saved_path
    return contract, raw_saved_path


def _fake_contract(filename: str | None, *, content_type: str | None = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", size_bytes: int | None = 1234) -> dict:
    workbook_ref = {
        "filename": filename,
        "workbook_id": "wb_fake",
        "attachment_id": "att_fake",
        "source": "upload",
        "content_type": content_type,
        "size_bytes": size_bytes,
        "saved_path": "/tmp/secret/local/workbook.xlsx",
    }
    return {"contract_id": "contract_fake", "workbook_ref": workbook_ref}


def test_alpha30_version_workbook_read_preflight_metadata() -> None:
    client = _alpha30_client()
    version = client.get("/api/version").json()
    assert version["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert version["scope"] == "workbook_read_policy_review_no_content_read"
    assert version["scope_metadata"]["workbook_read_preflight_contract"] is True
    assert version["scope_metadata"]["workbook_read_preflight_metadata_only"] is True
    assert version["scope_metadata"]["workbook_parse_enabled"] is False
    assert version["execution_locks"]["workbook_read_enabled"] is False
    assert version["execution_locks"]["builder_engine_execution_enabled"] is False
    assert version["execution_locks"]["legacy_builder_callable"] is False
    assert version["execution_locks"]["excel_output_enabled"] is False


def test_alpha30_no_contract_blocks_without_workbook_access() -> None:
    client = _alpha30_client()
    data = client.post(
        "/api/builder/workbook-read-preflight-dry-run",
        json={"conversation_id": "smoke_alpha30_no_contract", "client_event_id": "preflight_no_contract"},
    ).json()
    assert data["route"] == "builder_workbook_read_preflight_dry_run"
    assert data["metadata_only"] is True
    assert data["preflight_only"] is True
    assert data["execution_enabled"] is False
    assert data["blocked"] is True
    assert data["reason"] == "engine_contract_not_found"
    assert data["contract_found"] is False
    assert data["workbook_ref_found"] is False
    assert data["workbook_opened"] is False
    assert data["workbook_read"] is False
    assert data["workbook_parsed"] is False
    assert data["sheet_names_read"] is False
    assert data["cells_read"] is False
    assert data["formulas_read"] is False
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False
    assert data["raw_path_value_returned"] is False
    assert data["forbidden_path_key_returned"] is False
    assert _alpha30_contains_forbidden_exact_key(data) is False


def test_alpha30_ready_contract_preflight_is_scrubbed_and_metadata_only() -> None:
    client = _alpha30_client()
    _contract, raw_saved_path = _alpha30_ready_contract(client, "smoke_alpha30_contract")
    data = client.post(
        "/api/builder/workbook-read-preflight-dry-run",
        json={"conversation_id": "smoke_alpha30_contract", "client_event_id": "preflight_contract"},
    ).json()
    assert data["route"] == "builder_workbook_read_preflight_dry_run"
    assert data["reason"] == "workbook_read_preflight_contract_only"
    assert data["contract_found"] is True
    assert data["workbook_ref_found"] is True
    assert data["filename"] == "Test.xlsx"
    assert data["extension"] == ".xlsx"
    assert data["extension_allowed"] is True
    assert data["workbook_metadata_valid"] is True
    assert data["workbook_metadata_complete"] is True
    assert data["workbook_candidate_metadata_complete"] is True
    assert data["workbook_candidate_allowed_by_metadata"] is False
    assert data["workbook_read_allowed"] is False
    assert data["workbook_open_allowed"] is False
    assert data["path_resolver_contract_available"] is True
    assert data["path_resolver_summary"]["raw_saved_path_present"] is True
    assert data["workbook_opened"] is False
    assert data["workbook_read"] is False
    assert data["workbook_parsed"] is False
    assert data["sheet_names_read"] is False
    assert data["cells_read"] is False
    assert data["formulas_read"] is False
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False
    assert data["raw_path_value_returned"] is False
    assert data["forbidden_path_key_returned"] is False
    assert data["safety"]["raw_path_value_returned"] is False
    assert data["safety"]["forbidden_path_key_returned"] is False
    assert _alpha30_contains_forbidden_exact_key(data) is False
    assert raw_saved_path not in json.dumps(data, sort_keys=True)


def test_alpha30_metadata_extension_policy_direct_contracts() -> None:
    xlsm = evaluate_workbook_read_preflight_dry_run(conversation_id="xlsm", contract=_fake_contract("Test.xlsm", content_type="application/vnd.ms-excel.sheet.macroEnabled.12"))
    assert xlsm["extension"] == ".xlsm"
    assert xlsm["extension_allowed"] is True
    assert xlsm["workbook_metadata_complete"] is True
    assert xlsm["workbook_candidate_metadata_complete"] is True
    assert xlsm["workbook_candidate_allowed_by_metadata"] is False
    assert xlsm["workbook_read_allowed"] is False
    assert xlsm["workbook_open_allowed"] is False
    for filename in ["Test.pdf", "Test.zip", "Test.csv"]:
        data = evaluate_workbook_read_preflight_dry_run(conversation_id=filename, contract=_fake_contract(filename))
        assert data["extension"] in {".pdf", ".zip", ".csv"}
        assert data["extension_allowed"] is False
        assert data["workbook_candidate_allowed_by_metadata"] is False
        assert data["reason"] == "workbook_extension_not_allowed"
        assert data["workbook_opened"] is False
        assert data["workbook_read"] is False
        assert data["workbook_parsed"] is False
        assert data["engine_called"] is False
        assert data["excel_created"] is False
        assert data["legacy_builder_called"] is False
        assert data["raw_path_value_returned"] is False
        assert data["forbidden_path_key_returned"] is False
        assert _alpha30_contains_forbidden_exact_key(data) is False
        assert "/tmp/secret/local/workbook.xlsx" not in json.dumps(data, sort_keys=True)


def test_alpha30_preflight_endpoint_owner_is_isolated() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    py_files = [p for p in (root / "jarvis_v5").rglob("*.py") if "__pycache__" not in p.parts]
    endpoint_refs = []
    logic_refs = []
    for path in py_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root).as_posix()
        if "workbook-read-preflight-dry-run" in text:
            endpoint_refs.append(rel)
        if "evaluate_workbook_read_preflight_dry_run" in text:
            logic_refs.append(rel)
    assert "jarvis_v5/app.py" in endpoint_refs
    assert "jarvis_v5/tools/builder/workbook_read_preflight_contract.py" in logic_refs
    runtime_logic_refs = [ref for ref in logic_refs if not ref.startswith("jarvis_v5/tests/")]
    assert runtime_logic_refs == [
        "jarvis_v5/app.py",
        "jarvis_v5/tools/builder/workbook_read_preflight_contract.py",
    ]
