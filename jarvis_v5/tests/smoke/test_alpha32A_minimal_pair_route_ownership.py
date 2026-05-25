from __future__ import annotations

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def _client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, text: str, cid: str, event: str = "evt") -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    ).json()


def _assert_no_execution(data: dict) -> None:
    assert data.get("workbook_read") in (False, None)
    assert data.get("engine_called") in (False, None)
    assert data.get("excel_created") in (False, None)
    assert data.get("legacy_builder_called") in (False, None)


def test_alpha32A_version_scope_and_safety_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["scope"] == "workbook_read_policy_review_no_content_read"
    assert data["scope_metadata"]["minimal_pair_route_ownership_hygiene"] is True
    assert data["scope_metadata"]["no_active_action_needs_active_task"] is True
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha32A_targeted_minimal_pair_routes_no_fallback() -> None:
    client = _client()
    cases = [
        ("Preview is broken.", "feedback_read_only"),
        ("Preview.", "no_active_action_needs_active_task"),
        ("Use Doors and Windows.", "choose_tool"),
        ("Explain safe workbook path resolver.", "general_stub"),
        ("Run safe workbook path resolver dry run.", "choose_tool"),
        ("I need a checklist for waterproofing.", "general_stub"),
    ]
    for idx, (text, expected_route) in enumerate(cases):
        data = _chat(client, text, f"alpha32A_target_{idx}")
        assert data["route"] == expected_route
        assert data["fallback_used"] is False
        assert data.get("plan_mutated") is False
        _assert_no_execution(data)

    preview = _chat(client, "Preview.", "alpha32A_preview_no_active")
    assert preview["requires_clarification"] is True
    assert preview["reason"] == "no_active_action_requires_active_task"

    doors = _chat(client, "Use Doors and Windows.", "alpha32A_doors_windows")
    assert doors["requires_clarification"] is True
    assert "builder" in doors.get("tool_candidates", [])

    resolver = _chat(client, "Run safe workbook path resolver dry run.", "alpha32A_resolver_no_active")
    assert resolver["requires_clarification"] is True
    assert resolver.get("workbook_read") in (False, None)
    assert resolver.get("engine_called") in (False, None)


def test_alpha32A_existing_minimal_pair_routes_still_have_owner() -> None:
    client = _client()
    samples = [
        "Explain XGETCOUNT.",
        "Use XGETCOUNT.",
        "What does value mean?",
        "Create a Schedule of Values.",
        "Estimate how long this will take.",
        "Build a cost estimate BOQ.",
        "Check grammar in this RFI.",
        "Check this workbook.",
        "The word window appears in UI issue.",
        "What is MPa?",
        "Unit m2.",
        "Build me a BOQ.",
        "Format this sentence only.",
        "Use Formatter on this workbook.",
    ]
    for idx, text in enumerate(samples):
        data = _chat(client, text, f"alpha32A_regression_{idx}")
        assert data["fallback_used"] is False, text
        _assert_no_execution(data)


def test_alpha32A_feedback_markers_do_not_steal_writing_help() -> None:
    client = _client()
    for idx, text in enumerate([
        "Rewrite this issue report.",
        "Make my bug report clearer.",
        "Clean this complaint wording.",
    ]):
        data = _chat(client, text, f"alpha32A_writing_{idx}")
        assert data["route"] == "general_stub"
        assert data["reason"] == "format_text_not_workbook"
        assert data["fallback_used"] is False
        assert data.get("plan_mutated") is False
        _assert_no_execution(data)


def test_alpha32A_safe_no_active_action_guard_does_not_create_task() -> None:
    client = _client()
    cid = "alpha32A_no_active_action_no_task"
    data = _chat(client, "Preview.", cid)
    assert data["route"] == "no_active_action_needs_active_task"
    assert data["fallback_used"] is False
    assert data["plan_mutated"] is False
    plan = client.get(f"/api/plan/{cid}").json()
    assert plan["active_task"]["found"] is False
    _assert_no_execution(data)
