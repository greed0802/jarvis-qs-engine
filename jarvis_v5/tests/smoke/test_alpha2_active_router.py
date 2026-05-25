from __future__ import annotations

import json
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


def create_task(c: TestClient, conversation_id: str = "alpha2_chat") -> dict:
    return c.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "text": "Build me a BOQ", "client_event_id": f"evt-create-{conversation_id}"},
    ).json()


def set_test_clarification(c: TestClient, conv: str, prompt: str = "Choose A or B.") -> dict:
    state = c.get(f"/api/state/{conv}").json()
    task = state["active_task"]
    clarification = {
        "clarification_id": "clar_test_choice",
        "task_id": task["task_id"],
        "type": "test_choice",
        "prompt": prompt,
        "options": ["A", "B", "Cancel"],
        "expected_answer_classes": ["a", "b", "cancel"],
        "resolver_name": "resolve_test_choice",
        "context": {},
        "repeats": 0,
        "max_repeats": 2,
        "status": "open",
    }
    task["pending_clarification"] = clarification
    task["status"] = "needs_clarification"
    task_path = config.ACTIVE_TASKS_DIR / f"{task['task_id']}.json"
    task_path.write_text(json.dumps(task, indent=2), encoding="utf-8")
    conv_state = state["conversation"]
    conv_state["pending_clarification_id"] = "clar_test_choice"
    conv_path = config.CONVERSATIONS_DIR / f"{conv}.json"
    conv_path.write_text(json.dumps(conv_state, indent=2), encoding="utf-8")
    return clarification


def test_review_stays_in_active_task():
    c = client()
    create_task(c)
    r = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Review", "client_event_id": "evt-review"})
    data = r.json()
    assert data["route"] == "active_task_review"
    assert data["active_task_status"] == "waiting_for_file"
    assert "Current task" in data["message"]


def test_preview_is_stubbed_not_general_fallback():
    c = client()
    create_task(c)
    data = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Preview", "client_event_id": "evt-preview"}).json()
    assert data["route"] == "active_task_preview_stub"
    assert data["blocked"] is True
    assert data["reason"] == "preview_engine_not_connected"


def test_export_is_stubbed_not_general_fallback():
    c = client()
    create_task(c)
    data = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Export", "client_event_id": "evt-export"}).json()
    assert data["route"] == "active_task_export_stub"
    assert data["blocked"] is True
    assert data["reason"] == "export_engine_not_connected"


def test_pending_clarification_blocks_preview_but_allows_review():
    c = client()
    create_task(c)
    set_test_clarification(c, "alpha2_chat")
    preview = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Preview", "client_event_id": "evt-pending-preview"}).json()
    assert preview["route"] == "clarification_blocked_action"
    assert preview["blocked"] is True
    assert preview["pending_clarification_id"] == "clar_test_choice"
    review = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Review", "client_event_id": "evt-pending-review"}).json()
    assert review["route"] == "active_task_review"
    assert review["blocked"] is False
    assert review["pending_clarification_id"] == "clar_test_choice"


def test_clarification_answer_resolves_and_clears_state():
    c = client()
    create_task(c)
    set_test_clarification(c, "alpha2_chat")
    data = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "A", "client_event_id": "evt-answer-a"}).json()
    assert data["route"] == "clarification_resolved"
    assert data["pending_clarification_id"] is None
    state = c.get("/api/state/alpha2_chat").json()
    assert state["conversation"]["pending_clarification_id"] is None
    assert state["active_task"]["pending_clarification"] is None
    assert state["active_task"]["status"] == "collecting"


def test_cancel_clarification_keeps_task_active():
    c = client()
    create_task(c)
    set_test_clarification(c, "alpha2_chat")
    data = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Cancel", "client_event_id": "evt-cancel-clar"}).json()
    assert data["route"] == "clarification_cancelled"
    assert data["pending_clarification_id"] is None
    state = c.get("/api/state/alpha2_chat").json()
    assert state["conversation"]["active_task_id"] is not None
    assert state["active_task"]["status"] == "collecting"


def test_cancel_task_clears_active_task():
    c = client()
    create_task(c)
    data = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Cancel task", "client_event_id": "evt-cancel-task"}).json()
    assert data["route"] == "active_task_cancelled"
    assert data["active_task_id"] is None
    state = c.get("/api/state/alpha2_chat").json()
    assert state["conversation"]["active_task_id"] is None


def test_feedback_still_read_only_and_duplicate_still_works():
    c = client()
    create_task(c)
    one = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Wrong, not working", "client_event_id": "evt-feedback"}).json()
    two = c.post("/api/chat", json={"conversation_id": "alpha2_chat", "text": "Wrong, not working", "client_event_id": "evt-feedback"}).json()
    assert one["route"] == "feedback_read_only"
    assert two["duplicate"] is True
    events = c.get("/api/events/alpha2_chat").json()["events"]
    assert len([e for e in events if e.get("client_event_id") == "evt-feedback"]) == 1
