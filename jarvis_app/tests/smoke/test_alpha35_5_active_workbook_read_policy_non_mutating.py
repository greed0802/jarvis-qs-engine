from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def _client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, cid: str, event: str, text: str) -> dict:
    response = client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    )
    assert response.status_code == 200
    return response.json()


def _start_builder(client: TestClient, cid: str) -> dict:
    data = _chat(client, cid, "start", "Build me a BOQ")
    assert data["route"] == "new_builder_task_shell"
    return data


def _assert_no_execution(data: dict) -> None:
    assert data.get("plan_mutated") is False
    assert data.get("fallback_used") is False
    assert data.get("workbook_read") in (False, None)
    assert data.get("workbook_content_read") in (False, None)
    assert data.get("cells_read") in (False, None)
    assert data.get("formulas_read") in (False, None)
    assert data.get("engine_called") in (False, None)
    assert data.get("excel_created") in (False, None)
    assert data.get("legacy_builder_called") in (False, None)
    safety = data.get("safety") or {}
    assert safety.get("workbook_read") is not True
    assert safety.get("engine_called") is not True
    assert safety.get("excel_created") is not True
    assert safety.get("legacy_builder_called") is not True


def test_alpha35_6_version_lock() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha35_6_active_workbook_read_policy_questions_are_non_mutating() -> None:
    client = _client()
    cases = [
        "What is the workbook read policy review?",
        "Why are cells_read and formulas_read false?",
        "What does current_access_tier mean?",
        "Explain sheet-name probe versus cell read",
        "Tell me why preview readiness must not upgrade",
        "What is future limited cell range read?",
        "Why is workbook_parse_enabled false?",
        "Explain formula token policy",
        "What is allowed after metadata probe?",
        "Explain next safe action for workbook reading",
        "Why is current tier sheet_name_probe_only?",
        "Explain the current workbook read safety boundary",
    ]
    for idx, message in enumerate(cases):
        cid = f"alpha35_6_active_policy_{idx}_{uuid4().hex}"
        _start_builder(client, cid)
        data = _chat(client, cid, f"policy_{idx}", message)
        assert data["route"] == "active_task_non_mutating_language"
        assert data["router_step"] == "active_task_non_mutating_language_gate"
        assert data.get("non_mutating_category") == "workbook_read_policy_help"
        _assert_no_execution(data)


def test_alpha35_6_active_setup_edit_still_mutates() -> None:
    client = _client()
    cid = f"alpha35_6_setup_edit_{uuid4().hex}"
    _start_builder(client, cid)
    data = _chat(client, cid, "setup_edit", "Use Wall Types")
    assert data["route"] == "active_task_slot_edit"
    assert data.get("plan_mutated") is True


def test_alpha35_6_active_actions_still_route_unchanged() -> None:
    client = _client()
    cid = f"alpha35_6_actions_{uuid4().hex}"
    _start_builder(client, cid)
    review = _chat(client, cid, "review", "Review")
    assert review["route"] in {"active_task_review", "active_task_review_stub", "builder_review_setup"}
    assert review.get("fallback_used") is False
