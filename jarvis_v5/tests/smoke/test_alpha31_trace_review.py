from fastapi.testclient import TestClient
from jarvis_v5.app import app


def test_reducer_result_in_response_trace_and_plan_endpoint(tmp_path, monkeypatch):
    c = TestClient(app)
    conv = "alpha31_test"
    r1 = c.post("/api/chat", json={"conversation_id": conv, "client_event_id": "a31_001", "text": "Build me a BOQ"})
    assert r1.status_code == 200

    r2 = c.post("/api/chat", json={"conversation_id": conv, "client_event_id": "a31_002", "text": "Zone 1: Old and New"})
    data = r2.json()
    assert data["route"] == "active_task_slot_edit"
    assert data["reducer_result"]["slot"] == "zones"
    assert data["reducer_result"]["action"] == "set"
    assert "dynamic_zones" in data["reducer_result"]["changed_slots"]

    c.post("/api/chat", json={"conversation_id": conv, "client_event_id": "a31_003", "text": "Add Same to Zone 1"})
    c.post("/api/chat", json={"conversation_id": conv, "client_event_id": "a31_004", "text": "Change Old to Toad"})
    resolved = c.post("/api/chat", json={"conversation_id": conv, "client_event_id": "a31_005", "text": "Confirm replace"}).json()
    assert resolved["intent"] == "CLARIFICATION_ANSWER"
    assert resolved["reducer_result"]["action"] == "replace_confirmed"
    assert "dynamic_zones" in resolved["reducer_result"]["changed_slots"]

    review = c.post("/api/chat", json={"conversation_id": conv, "client_event_id": "a31_006", "text": "Review"}).json()
    assert "Current Builder shell task" in review["message"]
    assert "Zone 1: Toad, New, Same" in review["message"]
    assert "Preview/export engines are not connected" in review["message"]

    plan = c.get(f"/api/plan/{conv}").json()
    assert plan["found"] is True
    assert plan["plan_summary"]["zones"][0]["values"] == ["Toad", "New", "Same"]

    trace = c.get(f"/api/debug/router-trace/{conv}").json()["trace"]
    zone_trace = next(t for t in trace if t["client_event_id"] == "a31_002")
    assert zone_trace["reducer"]["slot"] == "zones"
    assert zone_trace["reducer"]["action"] == "set"
    assert "dynamic_zones" in zone_trace["reducer"]["changed_slots"]


def test_plan_endpoint_no_active_task():
    c = TestClient(app)
    data = c.get("/api/plan/no_such_conversation").json()
    assert data["found"] is False
