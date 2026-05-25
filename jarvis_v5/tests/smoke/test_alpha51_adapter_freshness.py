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


def adapter_dry_run(c, conversation_id: str, event_id: str) -> dict:
    return c.post(
        "/api/builder/adapter-dry-run",
        json={"conversation_id": conversation_id, "client_event_id": event_id},
    ).json()


def test_adapter_dry_run_marked_stale_when_source_snapshot_becomes_stale():
    c = client()
    conv = "alpha51_freshness"

    post_chat(c, conv, "a51_001", "Build me a BOQ")
    post_chat(c, conv, "a51_002", "Zone 1: Old and New")
    create_snapshot(c, conv, "a51_snap_001")
    dry = adapter_dry_run(c, conv, "a51_adapter_001")
    assert dry["blocked"] is False
    assert dry["adapter"]["freshness"] == "current"

    post_chat(c, conv, "a51_003", "Add Same to Zone 1")

    plan = c.get(f"/api/plan/{conv}").json()
    assert plan["plan_summary"]["zones"][0]["values"] == ["Old", "New", "Same"]
    assert plan["snapshot"]["status"] == "stale"
    assert plan["adapter_dry_run"]["found"] is True
    assert plan["adapter_dry_run"]["status"] == "stale_due_to_snapshot"
    assert plan["adapter_dry_run"]["freshness"] == "stale"
    assert plan["adapter_dry_run"]["stale_reason"] == "source_snapshot_is_stale"
    assert plan["adapter_dry_run"]["valid_for_dry_run"] is False
    assert plan["adapter_dry_run"]["engine_called"] is False
    assert plan["adapter_dry_run"]["excel_created"] is False

    review = post_chat(c, conv, "a51_004", "Review")
    assert "Builder Adapter Dry Run" in review["message"]
    assert "Freshness: stale" in review["message"]
    assert "Action needed: Create a new Builder snapshot" in review["message"]
    assert review["adapter"]["freshness"] == "stale"

    blocked = adapter_dry_run(c, conv, "a51_adapter_002")
    assert blocked["blocked"] is True
    assert blocked["reason"] == "snapshot_is_stale"
    assert blocked["adapter_dry_run"]["freshness"] == "stale"


def test_new_snapshot_refreshes_adapter_freshness():
    c = client()
    conv = "alpha51_refresh"

    post_chat(c, conv, "a51r_001", "Build me a BOQ")
    post_chat(c, conv, "a51r_002", "Zone 1: Old and New")
    create_snapshot(c, conv, "a51r_snap_001")
    adapter_dry_run(c, conv, "a51r_adapter_001")
    post_chat(c, conv, "a51r_003", "Add Same to Zone 1")

    create_snapshot(c, conv, "a51r_snap_002")
    dry = adapter_dry_run(c, conv, "a51r_adapter_002")
    assert dry["blocked"] is False
    assert dry["adapter"]["freshness"] == "current"
    assert dry["adapter_input"]["dynamic_zones"][0]["values"] == ["Old", "New", "Same"]
    assert dry["engine_called"] is False
    assert dry["excel_created"] is False

    plan = c.get(f"/api/plan/{conv}").json()
    assert plan["snapshot"]["status"] == "current"
    assert plan["adapter_dry_run"]["freshness"] == "current"
