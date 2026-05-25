from fastapi.testclient import TestClient

from jarvis_v5.app import app


def client():
    return TestClient(app)


def post_chat(c, conversation_id: str, event_id: str, text: str) -> dict:
    return c.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "text": text},
    ).json()


def create_snapshot(c, conversation_id: str, event_id: str) -> dict:
    return c.post(
        "/api/builder/create-snapshot",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "approve": True},
    ).json()


def adapter_dry_run(c, conversation_id: str, event_id: str, **extra) -> dict:
    payload = {"conversation_id": conversation_id, "client_event_id": event_id}
    payload.update(extra)
    return c.post("/api/builder/adapter-dry-run", json=payload).json()


def test_adapter_dry_run_uses_current_snapshot_without_engine_or_excel():
    c = client()
    conv = "alpha5_adapter"
    post_chat(c, conv, "a5_001", "Build me a BOQ")
    post_chat(c, conv, "a5_002", "Zone 1: Old and New")
    snap = create_snapshot(c, conv, "a5_snap_001")
    assert snap["snapshot_status"] == "current"

    dry = adapter_dry_run(c, conv, "a5_adapter_001")
    assert dry["route"] == "builder_adapter_dry_run"
    assert dry["blocked"] is False
    assert dry["engine_called"] is False
    assert dry["excel_created"] is False
    assert dry["adapter_input"]["dynamic_zones"][0]["values"] == ["Old", "New"]
    assert dry["validation"]["valid_for_dry_run"] is True
    assert dry["validation"]["valid_for_future_engine"] is False

    plan = c.get(f"/api/plan/{conv}").json()
    assert plan["adapter_dry_run"]["found"] is True
    assert plan["adapter_dry_run"]["engine_called"] is False
    assert plan["adapter_dry_run"]["excel_created"] is False

    trace = c.get(f"/api/debug/router-trace/{conv}").json()["trace"]
    row = next(row for row in trace if row["client_event_id"] == "a5_adapter_001")
    assert row["adapter"]["snapshot_id"] == snap["snapshot_id"]
    assert row["adapter"]["engine_called"] is False
    assert row["adapter"]["excel_created"] is False


def test_adapter_dry_run_blocks_stale_snapshot_until_new_snapshot_created():
    c = client()
    conv = "alpha5_stale"
    post_chat(c, conv, "a5s_001", "Build me a BOQ")
    post_chat(c, conv, "a5s_002", "Zone 1: Old and New")
    create_snapshot(c, conv, "a5s_snap_001")
    post_chat(c, conv, "a5s_003", "Add Same to Zone 1")

    blocked = adapter_dry_run(c, conv, "a5s_adapter_001")
    assert blocked["route"] == "builder_adapter_dry_run_blocked"
    assert blocked["blocked"] is True
    assert blocked["reason"] == "snapshot_is_stale"
    assert blocked["engine_called"] is False
    assert blocked["excel_created"] is False

    create_snapshot(c, conv, "a5s_snap_002")
    dry = adapter_dry_run(c, conv, "a5s_adapter_002")
    assert dry["blocked"] is False
    assert dry["adapter_input"]["dynamic_zones"][0]["values"] == ["Old", "New", "Same"]


def test_adapter_dry_run_blocks_pending_clarification():
    c = client()
    conv = "alpha5_pending"
    post_chat(c, conv, "a5p_001", "Build me a BOQ")
    post_chat(c, conv, "a5p_002", "Zone 1: Old and New")
    create_snapshot(c, conv, "a5p_snap_001")
    post_chat(c, conv, "a5p_003", "Change Old to Toad")

    blocked = adapter_dry_run(c, conv, "a5p_adapter_001")
    assert blocked["route"] == "builder_adapter_dry_run_blocked"
    assert blocked["blocked"] is True
    assert blocked["reason"] == "pending_clarification_blocks_adapter_dry_run"
    assert blocked["engine_called"] is False
    assert blocked["excel_created"] is False


def test_preview_export_remain_stubs_after_adapter_dry_run():
    c = client()
    conv = "alpha5_preview_stub"
    post_chat(c, conv, "a5v_001", "Build me a BOQ")
    post_chat(c, conv, "a5v_002", "Zone 1: Old and New")
    create_snapshot(c, conv, "a5v_snap_001")
    adapter_dry_run(c, conv, "a5v_adapter_001")

    preview = post_chat(c, conv, "a5v_003", "Preview")
    assert preview["route"] == "active_task_preview_stub"
    assert preview["blocked"] is True
    assert preview["reason"] == "preview_engine_not_connected"
