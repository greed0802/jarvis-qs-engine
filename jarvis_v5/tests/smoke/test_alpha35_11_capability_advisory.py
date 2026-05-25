from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.registry.registry_loader import requirement_check


def _client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, text: str, *, cid: str | None = None, event: str | None = None) -> dict:
    conversation_id = cid or f"alpha35_11_{uuid4().hex}"
    return client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": event or uuid4().hex, "text": text},
    ).json()


def _assert_no_execution(payload: dict) -> None:
    assert payload.get("fallback_used") is False
    assert payload.get("workbook_read") in (False, None)
    assert payload.get("engine_called") in (False, None)
    assert payload.get("excel_created") in (False, None)
    assert payload.get("legacy_builder_called") in (False, None)
    safety = payload.get("safety") or {}
    assert safety.get("workbook_read", False) is False
    assert safety.get("engine_called", False) is False
    assert safety.get("excel_created", False) is False
    assert safety.get("legacy_builder_called", False) is False


def _assert_registry_advisory(payload: dict, advisory_type: str) -> None:
    assert payload["route"] == "registry_advisory_metadata_only"
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
    _assert_no_execution(payload)


def test_alpha35_11_version_and_registry_locks() -> None:
    client = _client()
    data = client.get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False

    for endpoint, collection in [
        ("/api/registry/capabilities", "capabilities"),
        ("/api/registry/tools", "tools"),
        ("/api/registry/scope-advisors", "scope_advisors"),
        ("/api/registry/file-requirements", "file_requirements"),
        ("/api/registry/rfi-templates", "rfi_templates"),
    ]:
        payload = client.get(endpoint).json()
        assert payload["metadata_only"] is True
        assert payload["execution_enabled"] is False
        assert payload["workbook_read"] is False
        assert payload["engine_called"] is False
        assert payload["excel_created"] is False
        assert payload["legacy_builder_called"] is False
        for item in payload.get(collection, []):
            assert item.get("execution_enabled", False) is False


def test_requirement_check_advisory_type_contract() -> None:
    cases = [
        ("What should I measure for waterproofing?", "qs_scope_advisory"),
        ("What files do I need for tiling?", "file_requirement_advisory"),
        ("What RFI should I ask for painting?", "rfi_template_advisory"),
        ("Which tool should handle old and revised BOQ comparison?", "capability_advisory"),
        ("Create a scope risk checklist from the fire report", "scope_risk_advisory"),
    ]
    for text, expected in cases:
        payload = requirement_check(text)
        assert payload["advisory_type"] == expected
        assert payload["advisory_route"] == expected
        assert payload["metadata_only"] is True
        assert payload["execution_enabled"] is False
        assert payload["builder_mutation_allowed"] is False
        assert payload["active_task_mutated"] is False
        assert payload["requires_file_read"] is False
        assert payload["workbook_read"] is False
        assert payload["engine_called"] is False
        assert payload["excel_created"] is False
        assert payload["legacy_builder_called"] is False


def test_no_active_advisory_routes_are_metadata_only() -> None:
    client = _client()
    for text, advisory_type in [
        ("What should I measure for waterproofing?", "qs_scope_advisory"),
        ("What files do I need for tiling?", "file_requirement_advisory"),
        ("What RFI should I ask for painting?", "rfi_template_advisory"),
        ("Which tool should handle old and revised BOQ comparison?", "capability_advisory"),
    ]:
        data = _chat(client, text)
        _assert_registry_advisory(data, advisory_type)
        assert data.get("plan_mutated") is False


def test_alpha35_11_targeted_regressions() -> None:
    client = _client()

    builder = _chat(client, "Build me a BOQ")
    assert builder["route"] == "new_builder_task_shell"
    assert builder["fallback_used"] is False

    preview = _chat(client, "Preview")
    assert preview["route"] == "no_active_action_needs_active_task"
    assert preview["fallback_used"] is False
    _assert_no_execution(preview)

    read = _chat(client, "Open workbook and read cells")
    assert read["route"] == "no_active_prompt_injection_safe_block"
    assert read["metadata_only"] is True
    assert read["execution_enabled"] is False
    _assert_no_execution(read)

    future_tool = _chat(client, "Run O&A now for old and revised BOQ")
    _assert_registry_advisory(future_tool, "capability_advisory")
    assert "future_tool_advisor" in future_tool["requirement_advisor"].get("tool_candidates", [])


def test_alpha35_10_2_writing_report_preview_false_positive_stays_fixed() -> None:
    client = _client()
    cid = f"alpha35_11_active_write_{uuid4().hex}"
    start = _chat(client, "Build me a BOQ", cid=cid, event="start")
    assert start["route"] == "new_builder_task_shell"

    writing = _chat(client, "Rewrite this issue report: Preview is broken after MPa.", cid=cid, event="write")
    assert writing["route"] == "active_task_non_mutating_language"
    assert writing["router_step"] == "active_task_non_mutating_language_gate"
    assert writing["route"] != "active_task_preview_stub"
    assert writing["route"] != "feedback_read_only"
    assert writing.get("plan_mutated") is False
    _assert_no_execution(writing)
