from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.registry.registry_loader import requirement_check


def _client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, text: str, *, cid: str | None = None, event: str | None = None) -> dict:
    return client.post(
        "/api/chat",
        json={
            "conversation_id": cid or f"alpha35_12_{uuid4().hex}",
            "client_event_id": event or uuid4().hex,
            "text": text,
        },
    ).json()


def _assert_no_execution(payload: dict) -> None:
    assert payload.get("workbook_read") in (False, None)
    assert payload.get("engine_called") in (False, None)
    assert payload.get("excel_created") in (False, None)
    assert payload.get("legacy_builder_called") in (False, None)
    safety = payload.get("safety") or {}
    assert safety.get("workbook_read", False) is False
    assert safety.get("engine_called", False) is False
    assert safety.get("excel_created", False) is False
    assert safety.get("legacy_builder_called", False) is False


def _assert_registry_advisory(payload: dict, advisory_type: str) -> dict:
    assert payload["route"] == "registry_advisory_metadata_only"
    assert payload["fallback_used"] is False
    assert payload["metadata_only"] is True
    assert payload["execution_enabled"] is False
    advisor = payload["requirement_advisor"]
    assert advisor["advisory_type"] == advisory_type
    assert advisor["advisory_route"] == advisory_type
    assert advisor["metadata_only"] is True
    assert advisor["execution_enabled"] is False
    assert advisor["builder_mutation_allowed"] is False
    assert advisor["active_task_mutated"] is False
    assert advisor["requires_file_read"] is False
    assert advisor["tool_execution_called"] is False
    _assert_no_execution(payload)
    return advisor


def test_alpha35_12_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_future_tool_execution_requests_are_metadata_only_blocked() -> None:
    client = _client()
    for text in [
        "Run O&A on this workbook",
        "Run Formatter on the Builder output",
        "Run QA Checker now",
        "Run Document Reader on this report",
        "Compare old and revised BOQ",
    ]:
        payload = _chat(client, text)
        advisor = _assert_registry_advisory(payload, "capability_advisory")
        assert advisor["future_tool_requested"] is True
        assert advisor["execution_requested"] is True
        assert advisor["execution_blocked"] is True
        assert advisor["blocked_reason"] == "future_tool_execution_disabled"
        assert advisor["tool_execution_called"] is False


def test_unknown_scope_requires_clarification_without_builder_start() -> None:
    client = _client()
    payload = _chat(client, "What should I measure for unicorn cladding?")
    advisor = _assert_registry_advisory(payload, "qs_scope_advisory")
    assert advisor["known_scope"] is False
    assert advisor["unknown_scope"] is True
    assert advisor["requires_clarification"] is True
    assert advisor["clarification_questions"]
    assert payload["route"] != "new_builder_task_shell"
    assert payload.get("plan_mutated") is False


def test_known_scope_does_not_trigger_unknown_scope() -> None:
    payload = requirement_check("What should I measure for waterproofing?")
    assert payload["advisory_type"] == "qs_scope_advisory"
    assert payload["known_scope"] is True
    assert payload["unknown_scope"] is False
    assert payload["execution_enabled"] is False
    assert payload["workbook_read"] is False


def test_no_active_route_precision_regressions() -> None:
    client = _client()
    builder = _chat(client, "Build me a BOQ")
    assert builder["route"] == "new_builder_task_shell"
    assert builder["fallback_used"] is False

    create_boq = _chat(client, "Create a Bill of Quantities")
    assert create_boq["route"] == "new_builder_task_shell"
    assert create_boq["fallback_used"] is False

    preview = _chat(client, "Preview")
    assert preview["route"] == "no_active_action_needs_active_task"
    assert preview["route"] != "registry_advisory_metadata_only"
    _assert_no_execution(preview)

    read = _chat(client, "Open workbook and read cells")
    assert read["route"] == "no_active_prompt_injection_safe_block"
    assert read["route"] != "registry_advisory_metadata_only"
    assert read["metadata_only"] is True
    assert read["execution_enabled"] is False
    _assert_no_execution(read)


def test_alpha35_10_2_writing_report_preview_false_positive_stays_fixed() -> None:
    client = _client()
    cid = f"alpha35_12_active_write_{uuid4().hex}"
    start = _chat(client, "Build me a BOQ", cid=cid, event="start")
    assert start["route"] == "new_builder_task_shell"

    writing = _chat(client, "Rewrite this issue report: Preview is broken after MPa.", cid=cid, event="write")
    assert writing["route"] == "active_task_non_mutating_language"
    assert writing["router_step"] == "active_task_non_mutating_language_gate"
    assert writing["route"] != "active_task_preview_stub"
    assert writing["route"] != "feedback_read_only"
    assert writing.get("plan_mutated") is False
    _assert_no_execution(writing)
