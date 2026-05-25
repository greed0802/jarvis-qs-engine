from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def _client() -> TestClient:
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
    safety = data.get("safety") or {}
    assert safety.get("workbook_read", False) is False
    assert safety.get("engine_called", False) is False
    assert safety.get("excel_created", False) is False
    assert safety.get("legacy_builder_called", False) is False


def test_alpha35_10_2_version_and_safety_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_writing_issue_report_with_preview_word_is_non_mutating_language() -> None:
    client = _client()
    for idx, phrase in enumerate(
        [
            "Rewrite this issue report: Preview is broken after MPa.",
            "Rewrite this issue report: sq.m failed.",
            "Polish this bug report: Preview is not opening.",
            "Reword this message: Preview looks broken.",
        ]
    ):
        cid = f"alpha35_10_2_write_{idx}_{uuid4().hex}"
        _start_builder(client, cid)
        data = _chat(client, cid, "write", phrase)
        assert data["route"] == "active_task_non_mutating_language"
        assert data["router_step"] == "active_task_non_mutating_language_gate"
        assert data["route"] != "active_task_preview_stub"
        assert data["route"] != "feedback_read_only"
        _assert_no_execution(data)


def test_real_feedback_and_real_preview_actions_still_route_correctly() -> None:
    client = _client()

    cid = f"alpha35_10_2_feedback_{uuid4().hex}"
    _start_builder(client, cid)
    feedback = _chat(client, cid, "feedback", "Preview is broken after wall area.")
    assert feedback["route"] == "feedback_read_only"
    assert feedback["router_step"] == "feedback_router"
    _assert_no_execution(feedback)

    preview_cases = [
        "Preview",
        "Open preview",
        "Generate preview",
        "Run preview",
        "Can I see the preview?",
    ]
    for idx, phrase in enumerate(preview_cases):
        cid = f"alpha35_10_2_preview_{idx}_{uuid4().hex}"
        _start_builder(client, cid)
        preview = _chat(client, cid, "preview", phrase)
        assert preview["route"] == "active_task_preview_stub"
        assert preview.get("plan_mutated") is False
        assert preview.get("fallback_used") is False
        assert preview.get("workbook_read") in (False, None)
        assert preview.get("engine_called") in (False, None)
        assert preview.get("excel_created") in (False, None)
        assert preview.get("legacy_builder_called") in (False, None)
