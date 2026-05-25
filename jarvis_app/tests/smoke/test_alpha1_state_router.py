from __future__ import annotations

from pathlib import Path
import shutil
from fastapi.testclient import TestClient

from jarvis_v5 import config


def reset_data() -> None:
    for folder in [config.CONVERSATIONS_DIR, config.ACTIVE_TASKS_DIR, config.ATTACHMENTS_DIR, config.EVENTS_DIR, config.OUTPUTS_DIR]:
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)


def client() -> TestClient:
    reset_data()
    from jarvis_v5.app import app
    return TestClient(app)


def test_create_builder_task_waiting_for_file():
    c = client()
    r = c.post("/api/chat", json={"text": "Build me a BOQ", "client_event_id": "evt-test-a"})
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] == "NEW_COMMAND"
    assert data["route"] == "new_builder_task_shell"
    assert data["active_task_status"] == "waiting_for_file"


def test_attachment_binds_to_waiting_task():
    c = client()
    first = c.post("/api/chat", json={"text": "Build me a BOQ", "client_event_id": "evt-test-b1"}).json()
    conv = first["conversation_id"]
    r = c.post(
        "/api/chat",
        json={
            "conversation_id": conv,
            "text": "Here",
            "client_event_id": "evt-test-b2",
            "attachments": [{"filename": "Test.xlsx", "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}],
        },
    )
    data = r.json()
    assert data["route"] == "attachment_bind"
    assert data["active_task_status"] == "collecting"
    state = c.get(f"/api/state/{conv}").json()
    assert state["active_task"]["workbook"]["filename"] == "Test.xlsx"


def test_feedback_is_read_only_and_does_not_mutate_task():
    c = client()
    first = c.post("/api/chat", json={"text": "Build me a BOQ", "client_event_id": "evt-test-c1"}).json()
    conv = first["conversation_id"]
    before = c.get(f"/api/state/{conv}").json()["active_task"]
    r = c.post("/api/chat", json={"conversation_id": conv, "text": "Wrong, preview not working", "client_event_id": "evt-test-c2"})
    data = r.json()
    after = c.get(f"/api/state/{conv}").json()["active_task"]
    assert data["intent"] == "FEEDBACK"
    assert data["route"] == "feedback_read_only"
    assert after["plan"] == before["plan"]
    assert after["status"] == before["status"]
    assert len(after["feedback_log"]) == 1


def test_pending_clarification_blocks_risky_action():
    c = client()
    first = c.post("/api/chat", json={"text": "Build me a BOQ", "client_event_id": "evt-test-d1"}).json()
    conv = first["conversation_id"]
    state = c.get(f"/api/state/{conv}").json()
    task = state["active_task"]
    task["pending_clarification"] = {"prompt": "Choose replace or add.", "type": "zone_replace"}
    task["status"] = "needs_clarification"
    task_path = config.ACTIVE_TASKS_DIR / f"{task['task_id']}.json"
    task_path.write_text(__import__("json").dumps(task, indent=2), encoding="utf-8")
    r = c.post("/api/chat", json={"conversation_id": conv, "text": "Preview", "client_event_id": "evt-test-d2"})
    data = r.json()
    assert data["route"] == "clarification_blocked_action"
    assert data["blocked"] is True
    assert "before preview/export" in data["message"]


def test_duplicate_event_returns_cached_response():
    c = client()
    one = c.post("/api/chat", json={"text": "Build me a BOQ", "client_event_id": "evt-test-e"}).json()
    two = c.post("/api/chat", json={"conversation_id": one["conversation_id"], "text": "Build me a BOQ", "client_event_id": "evt-test-e"}).json()
    assert two["duplicate"] is True
    assert one["conversation_id"] == two["conversation_id"]
    events = c.get(f"/api/events/{one['conversation_id']}").json()["events"]
    assert len([e for e in events if e.get("client_event_id") == "evt-test-e"]) == 1


def test_preserves_valid_conversation_id_on_first_request():
    c = client()
    r = c.post(
        "/api/chat",
        json={
            "conversation_id": "test_alpha1_chat",
            "text": "Build me a BOQ",
            "client_event_id": "evt-test-preserve",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["conversation_id"] == "test_alpha1_chat"
    state = c.get("/api/state/test_alpha1_chat").json()
    assert state["found"] is True
    assert state["conversation"]["conversation_id"] == "test_alpha1_chat"


def test_placeholder_conversation_id_generates_chat_id():
    c = client()
    r = c.post(
        "/api/chat",
        json={
            "conversation_id": "string",
            "text": "Build me a BOQ",
            "client_event_id": "evt-test-placeholder",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["conversation_id"].startswith("chat_")
    assert data["conversation_id"] != "string"
    assert c.get("/api/state/string").json()["found"] is False


def test_blank_conversation_id_generates_chat_id():
    c = client()
    r = c.post(
        "/api/chat",
        json={
            "conversation_id": "",
            "text": "Build me a BOQ",
            "client_event_id": "evt-test-blank",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["conversation_id"].startswith("chat_")
