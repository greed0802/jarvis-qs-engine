from __future__ import annotations

import shutil
from fastapi.testclient import TestClient
from jarvis_v5 import config


def reset_data() -> None:
    for folder in [config.CONVERSATIONS_DIR, config.ACTIVE_TASKS_DIR, config.ATTACHMENTS_DIR, config.EVENTS_DIR, config.OUTPUTS_DIR, config.SNAPSHOTS_DIR]:
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)


def client() -> TestClient:
    reset_data()
    from jarvis_v5.app import app
    return TestClient(app)


def post(c: TestClient, text: str, event: str, conv: str = "alpha3_chat") -> dict:
    return c.post("/api/chat", json={"conversation_id": conv, "text": text, "client_event_id": event}).json()


def create_task(c: TestClient, conv: str = "alpha3_chat") -> dict:
    return post(c, "Build me a BOQ", "evt-create", conv)


def state(c: TestClient, conv: str = "alpha3_chat") -> dict:
    return c.get(f"/api/state/{conv}").json()


def plan(c: TestClient, conv: str = "alpha3_chat") -> dict:
    return state(c, conv)["active_task"]["plan"]


def test_zone_set_review():
    c = client()
    create_task(c)
    data = post(c, "Zone 1: Old and New", "evt-zone-set")
    assert data["route"] == "active_task_slot_edit"
    assert data["intent"] == "SLOT_EDIT"
    assert data["reducer_result"]["slot"] == "zones"
    p = plan(c)
    assert p["dynamic_zones"][0]["zone_id"] == 1
    assert p["dynamic_zones"][0]["values"] == ["Old", "New"]
    review = post(c, "Review", "evt-review")
    assert "Zone 1: Old, New" in review["message"]


def test_zone_append_and_explicit_replace():
    c = client()
    create_task(c)
    post(c, "Zone 1: Old and New", "evt-zone-set")
    post(c, "Add Same to Zone 1", "evt-zone-add")
    p = plan(c)
    assert p["dynamic_zones"][0]["values"] == ["Old", "New", "Same"]
    data = post(c, "Replace Old with Toad in Zone 1", "evt-zone-replace")
    assert data["route"] == "active_task_slot_edit"
    assert data["reducer_result"]["action"] == "replace"
    p = plan(c)
    assert p["dynamic_zones"][0]["values"] == ["Toad", "New", "Same"]


def test_ambiguous_replace_creates_clarification_and_blocks_preview_then_resolves():
    c = client()
    create_task(c)
    post(c, "Zone 1: Old and New", "evt-zone-set")
    data = post(c, "Change New to Fresh", "evt-ambiguous")
    assert data["route"] == "active_task_slot_edit_needs_clarification"
    assert data["pending_clarification_id"]
    preview = post(c, "Preview", "evt-preview-pending")
    assert preview["route"] == "clarification_blocked_action"
    assert preview["blocked"] is True
    resolved = post(c, "Confirm replace", "evt-confirm-replace")
    assert resolved["route"] == "clarification_resolved"
    assert resolved["intent"] == "CLARIFICATION_ANSWER"
    assert resolved["pending_clarification_id"] is None
    p = plan(c)
    assert p["dynamic_zones"][0]["values"] == ["Old", "Fresh"]


def test_level_set():
    c = client()
    create_task(c)
    data = post(c, "Levels GF to L3", "evt-levels")
    assert data["route"] == "active_task_slot_edit"
    assert data["reducer_result"]["slot"] == "levels"
    assert plan(c)["levels"] == ["GF", "L1", "L2", "L3"]


def test_trade_function_unit_state_only():
    c = client()
    create_task(c)
    assert post(c, "Use Doors and Windows", "evt-trade")["route"] == "active_task_slot_edit"
    assert post(c, "Use Count", "evt-count")["route"] == "active_task_slot_edit"
    assert post(c, "Unit no", "evt-unit")["route"] == "active_task_slot_edit"
    p = plan(c)
    assert p["trade_profile"] == "Doors / Windows"
    assert p["costx_function"] == "XGETCOUNT"
    assert p["unit"] == "no"


def test_feedback_preview_duplicate_still_safe():
    c = client()
    create_task(c)
    post(c, "Zone 1: Old and New", "evt-zone-set")
    before = plan(c)
    one = post(c, "Wrong, zone not working", "evt-feedback")
    two = post(c, "Wrong, zone not working", "evt-feedback")
    assert one["route"] == "feedback_read_only"
    assert two["duplicate"] is True
    assert plan(c) == before
    preview = post(c, "Preview", "evt-preview")
    assert preview["route"] == "active_task_preview_stub"
    assert preview["blocked"] is True
    assert preview["reason"] == "preview_engine_not_connected"


def test_dirty_zone_instruction_boundary():
    c = client()
    create_task(c)
    data = post(c, "Zone 2: External and Internal Use Head 3 for Zone 2", "evt-dirty")
    assert data["route"] == "active_task_slot_edit"
    p = plan(c)
    assert p["dynamic_zones"][0]["values"] == ["External", "Internal"]
    assert "Internal Use" not in p["dynamic_zones"][0]["values"]
