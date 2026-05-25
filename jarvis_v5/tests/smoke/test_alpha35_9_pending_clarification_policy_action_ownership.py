from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def _client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, conversation_id: str, event: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": event, "text": text},
    ).json()


def _start_pending_trade(client: TestClient, trade_text: str) -> tuple[str, dict]:
    conv = f"alpha35_10_pending_{uuid4().hex}"
    start = _chat(client, conv, f"{conv}_start", "Build me a BOQ")
    assert start["route"] == "new_builder_task_shell"
    pending = _chat(client, conv, f"{conv}_trade", trade_text)
    assert pending["route"] == "active_task_slot_edit_needs_clarification"
    assert pending["pending_clarification_id"]
    assert pending["reducer_result"]["plan_mutated"] is False
    return conv, pending


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


def test_pending_direct_cell_read_blocks_and_preserves_joinery_clarification() -> None:
    client = _client()
    conv, pending = _start_pending_trade(client, "Use Joinery")
    data = _chat(client, conv, f"{conv}_read_cells", "Read cells after approval")
    assert data["route"] == "clarification_blocked_action"
    assert data["blocked"] is True
    assert data["pending_clarification_id"] == pending["pending_clarification_id"]
    assert data["active_task_status"] == "needs_clarification"
    assert data.get("reducer_result") is None
    _assert_no_engine_safety(data)


def test_pending_workbook_open_list_sheets_blocks_and_preserves_painting_clarification() -> None:
    client = _client()
    conv, pending = _start_pending_trade(client, "Use Painting")
    data = _chat(client, conv, f"{conv}_open_sheets", "Open workbook and list sheets")
    assert data["route"] == "clarification_blocked_action"
    assert data["blocked"] is True
    assert data["pending_clarification_id"] == pending["pending_clarification_id"]
    assert data["active_task_status"] == "needs_clarification"
    _assert_no_engine_safety(data)


def test_pending_workbook_read_preflight_blocks_and_preserves_clarification() -> None:
    client = _client()
    conv, pending = _start_pending_trade(client, "Use Joinery")
    data = _chat(client, conv, f"{conv}_preflight", "Run workbook read preflight")
    assert data["route"] == "clarification_blocked_action"
    assert data["blocked"] is True
    assert data["pending_clarification_id"] == pending["pending_clarification_id"]
    assert data["active_task_status"] == "needs_clarification"
    _assert_no_engine_safety(data)


def test_pending_workbook_read_policy_review_is_allowed_read_only_and_preserves_clarification() -> None:
    client = _client()
    conv, pending = _start_pending_trade(client, "Use Painting")
    data = _chat(client, conv, f"{conv}_policy", "Review workbook read policy")
    assert data["route"] == "builder_workbook_read_policy_review"
    assert data["blocked"] is False
    assert data["fallback_used"] is False
    assert data["pending_clarification_id"] == pending["pending_clarification_id"]
    assert data["active_task_status"] == "needs_clarification"
    assert data["reducer_result"]["plan_mutated"] is False
    assert data["reducer_result"]["pending_clarification_preserved"] is True
    assert data["workbook_read"] is False
    assert data["policy_only"] is True
    _assert_no_engine_safety(data)


def test_pending_preview_and_export_blocks_remain_unchanged() -> None:
    client = _client()
    conv, pending = _start_pending_trade(client, "Use Joinery")
    preview = _chat(client, conv, f"{conv}_preview", "Preview")
    assert preview["route"] == "clarification_blocked_action"
    assert preview["blocked"] is True
    assert preview["pending_clarification_id"] == pending["pending_clarification_id"]
    export = _chat(client, conv, f"{conv}_export", "Export")
    assert export["route"] == "clarification_blocked_action"
    assert export["blocked"] is True
    assert export["pending_clarification_id"] == pending["pending_clarification_id"]
    _assert_no_engine_safety(preview)
    _assert_no_engine_safety(export)
