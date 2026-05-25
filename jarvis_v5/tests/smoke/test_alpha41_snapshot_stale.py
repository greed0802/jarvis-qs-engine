from fastapi.testclient import TestClient

from jarvis_v5.app import app


def client():
    return TestClient(app)


def post(c, conversation_id: str, event_id: str, text: str) -> dict:
    return c.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "text": text},
    ).json()


def create_snapshot(c, conversation_id: str, event_id: str) -> dict:
    return c.post(
        "/api/builder/create-snapshot",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "approve": True},
    ).json()


def test_snapshot_stales_when_plan_changes_after_snapshot():
    c = client()
    conv = "alpha41_stale"
    post(c, conv, "a41_001", "Build me a BOQ")
    post(c, conv, "a41_002", "Zone 1: Old and New")

    snap = create_snapshot(c, conv, "a41_snap_001")
    assert snap["route"] == "builder_snapshot_created"
    assert snap["snapshot_status"] == "current"
    assert snap["snapshot"]["dynamic_zones"][0]["values"] == ["Old", "New"]

    changed = post(c, conv, "a41_003", "Add Same to Zone 1")
    assert changed["route"] == "active_task_slot_edit"
    assert changed["snapshot"]["status"] == "stale"
    assert changed["snapshot"]["stale_reason"] == "active_plan_changed_after_snapshot"
    assert "snapshot is now stale" in changed["message"]

    active = c.get(f"/api/builder/active-snapshot/{conv}").json()
    assert active["found"] is True
    assert active["snapshot_status"] == "stale"
    assert active["stale_reason"] == "active_plan_changed_after_snapshot"
    # Snapshot remains frozen at the approved values.
    assert active["snapshot"]["dynamic_zones"][0]["values"] == ["Old", "New"]

    plan = c.get(f"/api/plan/{conv}").json()
    assert plan["snapshot"]["found"] is True
    assert plan["snapshot"]["status"] == "stale"
    assert plan["plan_summary"]["zones"][0]["values"] == ["Old", "New", "Same"]


def test_new_snapshot_after_stale_becomes_current_and_supersedes_old_active():
    c = client()
    conv = "alpha41_new_snapshot"
    post(c, conv, "a41n_001", "Build me a BOQ")
    post(c, conv, "a41n_002", "Zone 1: Old and New")
    old_snap = create_snapshot(c, conv, "a41n_snap_001")
    old_id = old_snap["snapshot_id"]

    post(c, conv, "a41n_003", "Add Same to Zone 1")
    new_snap = create_snapshot(c, conv, "a41n_snap_002")
    assert new_snap["snapshot_status"] == "current"
    assert new_snap["snapshot"]["dynamic_zones"][0]["values"] == ["Old", "New", "Same"]

    old = c.get(f"/api/builder/snapshot/{old_id}").json()
    assert old["found"] is True
    assert old["snapshot"]["status"] in {"stale", "superseded"}

    active = c.get(f"/api/builder/active-snapshot/{conv}").json()
    assert active["snapshot_status"] == "current"
    assert active["snapshot"]["snapshot_id"] == new_snap["snapshot_id"]


def test_router_trace_includes_snapshot_metadata_for_edit_and_preview():
    c = client()
    conv = "alpha41_trace"
    post(c, conv, "a41t_001", "Build me a BOQ")
    post(c, conv, "a41t_002", "Zone 1: Old and New")
    create_snapshot(c, conv, "a41t_snap_001")
    post(c, conv, "a41t_003", "Add Same to Zone 1")
    preview = post(c, conv, "a41t_004", "Preview")
    assert preview["route"] == "active_task_preview_stub"
    assert preview["blocked"] is True
    assert preview["snapshot"]["status"] == "stale"
    assert "snapshot is stale" in preview["message"]

    trace = c.get(f"/api/debug/router-trace/{conv}").json()["trace"]
    edit_row = next(row for row in trace if row["client_event_id"] == "a41t_003")
    assert edit_row["snapshot"]["status"] == "stale"
    assert edit_row["snapshot"]["stale_reason"] == "active_plan_changed_after_snapshot"
    preview_row = next(row for row in trace if row["client_event_id"] == "a41t_004")
    assert preview_row["snapshot"]["status"] == "stale"
