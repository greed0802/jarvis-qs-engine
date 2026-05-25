from __future__ import annotations

import shutil
from fastapi.testclient import TestClient
from jarvis_v5 import config


def reset_data() -> None:
    for folder in [
        config.CONVERSATIONS_DIR,
        config.ACTIVE_TASKS_DIR,
        config.ATTACHMENTS_DIR,
        config.EVENTS_DIR,
        config.OUTPUTS_DIR,
        config.SNAPSHOTS_DIR,
    ]:
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)


def client() -> TestClient:
    reset_data()
    from jarvis_v5.app import app
    return TestClient(app)


def post(c: TestClient, conv: str, event: str, text: str) -> dict:
    return c.post("/api/chat", json={"conversation_id": conv, "client_event_id": event, "text": text}).json()


def test_create_snapshot_from_active_plan_and_get_active_snapshot():
    c = client()
    conv = "alpha4_snapshot"
    post(c, conv, "a4_001", "Build me a BOQ")
    post(c, conv, "a4_002", "Zone 1: Old and New")

    snap = c.post("/api/builder/create-snapshot", json={"conversation_id": conv, "client_event_id": "a4_snap_001", "approve": True}).json()
    assert snap["route"] == "builder_snapshot_created"
    assert snap["blocked"] is False
    assert snap["valid"] is True
    assert snap["snapshot_id"].startswith("snap_")
    assert snap["snapshot_hash"]
    assert snap["snapshot"]["source"] == "active_task"
    assert snap["snapshot"]["dynamic_zones"][0]["values"] == ["Old", "New"]
    assert "No workbook attached" in snap["validation"]["warnings"]

    by_id = c.get(f"/api/builder/snapshot/{snap['snapshot_id']}").json()
    assert by_id["found"] is True
    assert by_id["snapshot"]["snapshot_hash"] == snap["snapshot_hash"]

    active = c.get(f"/api/builder/active-snapshot/{conv}").json()
    assert active["found"] is True
    assert active["snapshot"]["snapshot_id"] == snap["snapshot_id"]

    trace = c.get(f"/api/debug/router-trace/{conv}").json()["trace"]
    row = next(t for t in trace if t["client_event_id"] == "a4_snap_001")
    assert row["route"] == "builder_snapshot_created"
    assert row["intent"] == "BUILDER_SNAPSHOT"


def test_pending_clarification_blocks_snapshot_until_resolved():
    c = client()
    conv = "alpha4_pending"
    post(c, conv, "a4p_001", "Build me a BOQ")
    post(c, conv, "a4p_002", "Zone 1: Old and New")
    pending = post(c, conv, "a4p_003", "Change Old to Toad")
    assert pending["pending_clarification_id"]

    blocked = c.post("/api/builder/create-snapshot", json={"conversation_id": conv, "client_event_id": "a4p_snap_blocked", "approve": True}).json()
    assert blocked["blocked"] is True
    assert blocked["reason"] == "pending_clarification_blocks_snapshot"

    resolved = post(c, conv, "a4p_004", "Confirm replace")
    assert resolved["route"] == "clarification_resolved"

    snap = c.post("/api/builder/create-snapshot", json={"conversation_id": conv, "client_event_id": "a4p_snap_ok", "approve": True}).json()
    assert snap["blocked"] is False
    assert snap["snapshot"]["dynamic_zones"][0]["values"] == ["Toad", "New"]


def test_preview_export_remain_stubs_with_snapshot():
    c = client()
    conv = "alpha4_preview_stub"
    post(c, conv, "a4s_001", "Build me a BOQ")
    post(c, conv, "a4s_002", "Zone 1: Old and New")
    c.post("/api/builder/create-snapshot", json={"conversation_id": conv, "client_event_id": "a4s_snap", "approve": True})

    preview = post(c, conv, "a4s_preview", "Preview")
    assert preview["route"] == "active_task_preview_stub"
    assert preview["blocked"] is True
    assert preview["reason"] == "preview_engine_not_connected"

    export = post(c, conv, "a4s_export", "Export")
    assert export["route"] == "active_task_export_stub"
    assert export["blocked"] is True
    assert export["reason"] == "export_engine_not_connected"
