from __future__ import annotations

from io import BytesIO
from fastapi.testclient import TestClient

from jarvis_v5.app import app


def client() -> TestClient:
    return TestClient(app)


def post_chat(c: TestClient, conversation_id: str, event_id: str, text: str) -> dict:
    return c.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "text": text},
    ).json()


def attach_workbook(c: TestClient, conversation_id: str, event_id: str, filename: str = "Steel test.xlsx") -> dict:
    return c.post(
        "/api/attach",
        data={"conversation_id": conversation_id, "client_event_id": event_id, "text": "Here"},
        files={"file": (filename, BytesIO(b"fake workbook bytes - not read"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    ).json()


def create_snapshot(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post(
        "/api/builder/create-snapshot",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "approve": True},
    ).json()


def adapter_dry_run(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post(
        "/api/builder/adapter-dry-run",
        json={"conversation_id": conversation_id, "client_event_id": event_id},
    ).json()


def test_attachment_binds_workbook_metadata_to_active_builder_task_without_reading():
    c = client()
    conv = "alpha6_attach_bind"
    start = post_chat(c, conv, "a6_001", "Build me a BOQ")
    assert start["active_task_status"] == "waiting_for_file"

    bind = attach_workbook(c, conv, "a6_attach_001")
    assert bind["route"] == "attachment_bind"
    assert bind["active_task_status"] == "collecting"
    assert bind["state"]["active_workbook_id"].startswith("att_")
    assert bind["reducer_result"]["workbook"]["filename"] == "Steel test.xlsx"
    assert bind["reducer_result"]["workbook_read"] is False

    state = c.get(f"/api/state/{conv}").json()
    workbook = state["active_task"]["workbook"]
    assert workbook["filename"] == "Steel test.xlsx"
    assert workbook["workbook_id"] == bind["state"]["active_workbook_id"]
    assert workbook["bound_to_task_id"] == start["active_task_id"]

    plan = c.get(f"/api/plan/{conv}").json()
    assert plan["workbook"]["found"] is True
    assert plan["workbook"]["filename"] == "Steel test.xlsx"
    assert "saved_path" not in plan["workbook"]


def test_snapshot_and_adapter_capture_workbook_ref_without_reading_workbook():
    c = client()
    conv = "alpha6_snapshot_adapter"
    post_chat(c, conv, "a6s_001", "Build me a BOQ")
    attach_workbook(c, conv, "a6s_attach_001")
    post_chat(c, conv, "a6s_002", "Zone 1: Old and New")

    snap = create_snapshot(c, conv, "a6s_snap_001")
    assert snap["snapshot_status"] == "current"
    assert snap["snapshot"]["workbook_ref"]["filename"] == "Steel test.xlsx"
    assert "No workbook attached" not in snap["validation"]["warnings"]

    dry = adapter_dry_run(c, conv, "a6s_adapter_001")
    assert dry["route"] == "builder_adapter_dry_run"
    assert dry["blocked"] is False
    assert dry["engine_called"] is False
    assert dry["excel_created"] is False
    assert dry["workbook_read"] is False
    assert dry["adapter_input"]["workbook_ref"]["filename"] == "Steel test.xlsx"
    assert dry["adapter_input"]["workbook_read"] is False

    plan = c.get(f"/api/plan/{conv}").json()
    assert plan["workbook"]["filename"] == "Steel test.xlsx"
    assert plan["snapshot"]["workbook_ref"]["filename"] == "Steel test.xlsx"
    assert plan["adapter_dry_run"]["workbook_read"] is False


def test_attachment_only_without_active_task_does_not_create_builder_task():
    c = client()
    conv = "alpha6_attach_no_task"
    resp = attach_workbook(c, conv, "a6n_attach_001")
    assert resp["route"] == "attachment_received_no_active_task"
    assert resp["active_task_id"] is None
    assert resp["state"]["active_task_id"] is None
    assert resp["reducer_result"]["workbook"]["filename"] == "Steel test.xlsx"
    assert resp["reducer_result"]["workbook_read"] is False


def test_duplicate_attachment_event_returns_cached_response_without_rebinding():
    c = client()
    conv = "alpha6_duplicate_attach"
    post_chat(c, conv, "a6d_001", "Build me a BOQ")
    first = attach_workbook(c, conv, "a6d_attach_001", filename="Steel test.xlsx")
    second = attach_workbook(c, conv, "a6d_attach_001", filename="Other.xlsx")
    assert second["duplicate"] is True
    assert second["state"]["active_workbook_id"] == first["state"]["active_workbook_id"]
    state = c.get(f"/api/state/{conv}").json()
    assert state["active_task"]["workbook"]["filename"] == "Steel test.xlsx"


def test_attachment_store_recreates_missing_directory_before_save():
    c = client()
    conv = "alpha61_missing_attachment_dir"
    post_chat(c, conv, "a61_001", "Build me a BOQ")

    from jarvis_v5.app import kernel
    import shutil
    shutil.rmtree(kernel.attachments.root, ignore_errors=True)
    assert not kernel.attachments.root.exists()

    bind = attach_workbook(c, conv, "a61_attach_001")
    assert bind["route"] == "attachment_bind"
    assert bind["active_task_status"] == "collecting"
    assert bind["state"]["active_workbook_id"].startswith("att_")
    assert kernel.attachments.root.exists()


def test_attachment_save_failure_returns_safe_json_without_task_mutation(monkeypatch):
    c = client()
    conv = "alpha61_safe_failure"
    start = post_chat(c, conv, "a61f_001", "Build me a BOQ")

    from jarvis_v5.app import kernel
    def boom(_file):
        raise FileNotFoundError("simulated missing folder")
    monkeypatch.setattr(kernel.attachments, "save_upload", boom)

    resp = attach_workbook(c, conv, "a61f_attach_001")
    assert resp["route"] == "attachment_save_failed"
    assert resp["blocked"] is True
    assert resp["reason"] == "attachment_save_failed"
    assert resp["active_task_id"] == start["active_task_id"]
    assert resp["reducer_result"]["workbook_read"] is False

    state = c.get(f"/api/state/{conv}").json()
    assert state["conversation"]["active_workbook_id"] is None
    assert state["active_task"]["workbook"] is None
