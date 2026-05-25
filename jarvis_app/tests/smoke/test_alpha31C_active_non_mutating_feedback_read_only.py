from __future__ import annotations

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def _alpha31c_client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, cid: str, event: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    ).json()


def _start_builder(client: TestClient, cid: str) -> None:
    data = _chat(client, cid, "start", "Build me a BOQ")
    assert data["route"] == "new_builder_task_shell"


def _assert_no_execution(data: dict) -> None:
    assert data.get("plan_mutated") is False
    assert data.get("fallback_used") is False
    assert data.get("workbook_read") in (False, None)
    assert data.get("engine_called") in (False, None)
    assert data.get("excel_created") in (False, None)
    assert data.get("legacy_builder_called") in (False, None)


def test_alpha31C_version_and_safety_locks() -> None:
    data = _alpha31c_client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["scope"] == "workbook_read_policy_review_no_content_read"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha31C_active_concept_questions_are_non_mutating() -> None:
    client = _alpha31c_client()
    phrases = [
        "Tell me why workbook_read must stay false.",
        "Explain the current safety boundary.",
        "What is an adapter dry run?",
        "Explain the contract-only stage.",
        "What does formula integrity guard mean?",
        "Why should preview be approval-based?",
        "What is a BuilderRunSnapshot?",
    ]
    for idx, phrase in enumerate(phrases):
        cid = f"alpha31C_concept_{idx}"
        _start_builder(client, cid)
        data = _chat(client, cid, "ask", phrase)
        assert data["route"] == "active_task_non_mutating_language"
        assert data["router_step"] == "active_task_non_mutating_language_gate"
        _assert_no_execution(data)


def test_alpha31C_active_feedback_is_read_only() -> None:
    client = _alpha31c_client()
    phrases = [
        "The workbook preflight wording looks wrong.",
        "There are no milestone levels in this setup.",
        "The window issue is UI feedback, not Doors and Windows.",
        "Open preview must close correctly.",
        "Why do you still fallback on correct actions?",
        "This is feedback only about active Builder.",
    ]
    for idx, phrase in enumerate(phrases):
        cid = f"alpha31C_feedback_{idx}"
        _start_builder(client, cid)
        data = _chat(client, cid, "feedback", phrase)
        assert data["route"] == "feedback_read_only"
        assert data["router_step"] == "feedback_router"
        _assert_no_execution(data)


def test_alpha31C_active_actions_still_work() -> None:
    client = _alpha31c_client()
    cases = [
        ("Preview it please.", "active_task_preview_stub"),
        ("Open preview.", "active_task_preview_stub"),
        ("Export it.", "active_task_export_stub"),
        ("Download output.", "active_task_action_stub"),
        ("Review current setup.", "active_task_review"),
    ]
    for idx, (phrase, expected_route) in enumerate(cases):
        cid = f"alpha31C_action_{idx}"
        _start_builder(client, cid)
        data = _chat(client, cid, "action", phrase)
        assert data["route"] == expected_route
        assert data["fallback_used"] is False
        assert data.get("plan_mutated") is False


def test_alpha31C_slot_edits_still_mutate() -> None:
    client = _alpha31c_client()
    for idx, phrase in enumerate(["Use Wall Types.", "Use Structural Steel.", "Unit m2."]):
        cid = f"alpha31C_slot_{idx}"
        _start_builder(client, cid)
        data = _chat(client, cid, "slot", phrase)
        assert data["route"] == "active_task_slot_edit"
        assert data["fallback_used"] is False
        assert data.get("plan_mutated") is True


def test_alpha31C_writing_help_not_stolen_as_feedback() -> None:
    client = _alpha31c_client()
    for idx, phrase in enumerate(["Rewrite this issue report.", "Make my bug report clearer."]):
        cid = f"alpha31C_writing_{idx}"
        _start_builder(client, cid)
        data = _chat(client, cid, "write", phrase)
        assert data["route"] == "active_task_non_mutating_language"
        assert data["route"] != "feedback_read_only"
        _assert_no_execution(data)
