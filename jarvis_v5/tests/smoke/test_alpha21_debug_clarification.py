from fastapi.testclient import TestClient

from jarvis_v5.app import app


def test_create_debug_clarification_requires_active_task():
    client = TestClient(app)
    resp = client.post(
        "/api/debug/create-test-clarification",
        json={"conversation_id": "no_task_chat", "client_event_id": "debug_no_task", "prompt": "Choose A or B."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["blocked"] is True
    assert data["reason"] in {"conversation_not_found", "no_active_task"}


def test_pending_clarification_manual_flow_and_router_trace():
    client = TestClient(app)
    conversation_id = "alpha21_smoke_chat"

    created = client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": "a21_evt_001", "text": "Build me a BOQ"},
    ).json()
    assert created["route"] == "new_builder_task_shell"
    assert created["active_task_status"] == "waiting_for_file"

    clar = client.post(
        "/api/debug/create-test-clarification",
        json={
            "conversation_id": conversation_id,
            "client_event_id": "debug_clar_001",
            "prompt": "Choose A or B.",
            "options": ["A", "B", "Cancel"],
        },
    ).json()
    assert clar["route"] == "debug_create_test_clarification"
    assert clar["blocked"] is False
    assert clar["pending_clarification_id"].startswith("clar_")

    pending = client.get(f"/api/debug/pending-clarification/{conversation_id}").json()
    assert pending["found"] is True
    assert pending["pending_clarification"]["status"] == "open"

    review = client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": "a21_evt_002", "text": "Review"},
    ).json()
    assert review["route"] == "active_task_review"
    assert review["blocked"] is False
    assert review["pending_clarification_id"] == clar["pending_clarification_id"]

    preview_block = client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": "a21_evt_003", "text": "Preview"},
    ).json()
    assert preview_block["route"] == "clarification_blocked_action"
    assert preview_block["blocked"] is True
    assert preview_block["reason"] == "pending_clarification_blocks_risky_action"
    assert preview_block["pending_clarification_id"] == clar["pending_clarification_id"]

    answer = client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": "a21_evt_004", "text": "A"},
    ).json()
    assert answer["route"] == "clarification_resolved"
    assert answer["intent"] == "CLARIFICATION_ANSWER"
    assert answer["blocked"] is False
    assert answer["pending_clarification_id"] is None

    preview_stub = client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": "a21_evt_005", "text": "Preview"},
    ).json()
    assert preview_stub["route"] == "active_task_preview_stub"
    assert preview_stub["blocked"] is True
    assert preview_stub["reason"] == "preview_engine_not_connected"

    trace = client.get(f"/api/debug/router-trace/{conversation_id}").json()["trace"]
    routes = [entry["route"] for entry in trace]
    assert "new_builder_task_shell" in routes
    assert "debug_create_test_clarification" in routes
    assert "active_task_review" in routes
    assert "clarification_blocked_action" in routes
    assert "clarification_resolved" in routes
    assert "active_task_preview_stub" in routes
    debug_entries = [entry for entry in trace if entry["route"] == "debug_create_test_clarification"]
    assert debug_entries
    assert debug_entries[0]["intent"] == "DEBUG"
    assert debug_entries[0]["text"] == "Choose A or B."
    resolved_entries = [entry for entry in trace if entry["route"] == "clarification_resolved"]
    assert resolved_entries and resolved_entries[0]["intent"] == "CLARIFICATION_ANSWER"
    blocked_entries = [entry for entry in trace if entry["route"] == "clarification_blocked_action"]
    assert blocked_entries and blocked_entries[0]["blocked"] is True


def test_cancel_clarification_clears_pending():
    client = TestClient(app)
    conversation_id = "alpha21_cancel_clar_chat"
    client.post("/api/chat", json={"conversation_id": conversation_id, "client_event_id": "cancel_evt_001", "text": "Build me a BOQ"})
    clar = client.post(
        "/api/debug/create-test-clarification",
        json={"conversation_id": conversation_id, "client_event_id": "cancel_debug_001", "prompt": "Choose A or B."},
    ).json()
    assert clar["pending_clarification_id"]
    cancelled = client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": "cancel_evt_002", "text": "Cancel"},
    ).json()
    assert cancelled["route"] == "clarification_cancelled"
    assert cancelled["pending_clarification_id"] is None
    pending = client.get(f"/api/debug/pending-clarification/{conversation_id}").json()
    assert pending["found"] is False
