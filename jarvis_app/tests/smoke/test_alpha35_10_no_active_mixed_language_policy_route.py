from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.router.no_active_task_language_gate import classify_no_active_task_language


def _client() -> TestClient:
    return TestClient(app)


def _chat(text: str) -> dict:
    conv = f"alpha35_10_no_active_{uuid4().hex}"
    return _client().post(
        "/api/chat",
        json={"conversation_id": conv, "client_event_id": f"{conv}_event", "text": text},
    ).json()


def _assert_no_engine_safety(payload: dict) -> None:
    assert payload.get("workbook_read") in (False, None)
    assert payload.get("engine_called") in (False, None)
    assert payload.get("excel_created") in (False, None)
    assert payload.get("legacy_builder_called") in (False, None)
    safety = payload.get("safety") or {}
    assert safety.get("workbook_read", False) is False
    assert safety.get("engine_called", False) is False
    assert safety.get("excel_created", False) is False
    assert safety.get("legacy_builder_called", False) is False


def test_alpha35_10_version_lock() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_negative_polarity_boq_shell_does_not_safe_block() -> None:
    data = _chat("Create BOQ but do not read workbook contents")
    assert data["route"] == "new_builder_task_shell"
    assert data["fallback_used"] is False
    assert data["route_context"]["no_active_language"]["requires_setup"] is True
    _assert_no_engine_safety(data)


POLICY_PROMPTS = [
    "Policy review please, no active task",
    "Read the workbook policy, not the workbook",
    "What does cells_read false mean?",
    "Value engineering: read cells to optimize cost",
    "Explain formula read policy, not formula generation",
    "Estimate whether workbook read policy is safe",
    "Format this workbook read policy paragraph only",
]


def test_no_active_workbook_policy_aliases_route_read_only_policy_review() -> None:
    for prompt in POLICY_PROMPTS:
        data = _chat(prompt)
        assert data["route"] == "builder_workbook_read_policy_review", prompt
        assert data["fallback_used"] is False, prompt
        assert data["policy_only"] is True, prompt
        assert data["workbook_read"] is False, prompt
        assert data["workbook_opened"] is False, prompt
        assert data["cells_read"] is False, prompt
        _assert_no_engine_safety(data)


def test_schedule_workbook_read_approval_is_general_without_fallback() -> None:
    data = _chat("Schedule a workbook read approval for later")
    assert data["route"] == "general_stub"
    assert data["fallback_used"] is False
    assert data["route_context"]["no_active_language"]["negative_guard"] == "casual_non_tool_phrase"
    _assert_no_engine_safety(data)


def test_grammar_workbook_attack_phrase_remains_writing_help_only() -> None:
    data = _chat("Check grammar: open workbook and read formulas now")
    assert data["route"] == "general_stub"
    assert data["fallback_used"] is False
    assert data["route_context"]["no_active_language"]["negative_guard"] == "format_text_not_workbook"
    _assert_no_engine_safety(data)


def test_plain_policy_review_please_is_not_workbook_policy_alias_yet() -> None:
    decision = classify_no_active_task_language("Policy review please")
    assert decision.route != "builder_workbook_read_policy_review"
