from __future__ import annotations

import json
from fastapi.testclient import TestClient

from jarvis_v5 import config
from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.tests.smoke.test_cleanup import safe_rmtree


def _reset_data() -> None:
    for folder in [
        config.CONVERSATIONS_DIR,
        config.ACTIVE_TASKS_DIR,
        config.ATTACHMENTS_DIR,
        config.OUTPUTS_DIR,
        config.EVENTS_DIR,
        config.SNAPSHOTS_DIR,
        config.ADAPTERS_DIR,
        config.CONTRACTS_DIR,
        config.PREFLIGHTS_DIR,
        config.EXECUTIONS_DIR,
        config.TEST_REPORTS_DIR,
    ]:
        if folder.exists():
            safe_rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)


def _client() -> TestClient:
    _reset_data()
    return TestClient(app)


def _start_builder(client: TestClient, cid: str) -> None:
    data = client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": f"{cid}_start", "text": "Build me a BOQ"},
    ).json()
    assert data["route"] == "new_builder_task_shell"


def _set_test_clarification(client: TestClient, cid: str) -> str:
    data = client.post(
        "/api/debug/create-test-clarification",
        json={
            "conversation_id": cid,
            "client_event_id": f"{cid}_debug_clarification",
            "prompt": "Choose A or B.",
            "options": ["A", "B", "Cancel"],
        },
    ).json()
    assert data["route"] == "debug_create_test_clarification"
    assert data["blocked"] is False
    assert data["pending_clarification_id"]
    return data["pending_clarification_id"]


def _open_pending(client: TestClient, cid: str) -> str:
    _start_builder(client, cid)
    return _set_test_clarification(client, cid)


def _post(client: TestClient, cid: str, event: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    ).json()


def _assert_no_execution(data: dict) -> None:
    assert data.get("plan_mutated") is False
    assert data.get("workbook_read") in (False, None)
    assert data.get("engine_called") in (False, None)
    assert data.get("excel_created") in (False, None)
    assert data.get("legacy_builder_called") in (False, None)


def test_alpha31D_version_and_safety_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["scope"] == "workbook_read_policy_review_no_content_read"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False
    assert data["scope_metadata"]["pending_clarification_risky_action_coverage"] is True


def test_alpha31D_pending_risky_actions_are_blocked() -> None:
    client = _client()
    phrases = [
        "Export current output",
        "Approve and preview",
        "Download output link",
        "Preview safely",
        "Run builder now",
    ]
    for idx, phrase in enumerate(phrases):
        cid = f"alpha31D_block_{idx}"
        pending_id = _open_pending(client, cid)
        data = _post(client, cid, f"block_{idx}", phrase)
        assert data["route"] == "clarification_blocked_action"
        assert data["blocked"] is True
        assert data["fallback_used"] is False
        assert data["reason"] == "pending_clarification_blocks_risky_action"
        assert data["pending_clarification_id"] == pending_id
        _assert_no_execution(data)


def test_alpha31D_pending_review_remains_allowed() -> None:
    client = _client()
    phrases = ["Review current setup", "Show setup", "Current setup"]
    for idx, phrase in enumerate(phrases):
        cid = f"alpha31D_review_{idx}"
        pending_id = _open_pending(client, cid)
        data = _post(client, cid, f"review_{idx}", phrase)
        assert data["route"] == "active_task_review"
        assert data["blocked"] is False
        assert data["fallback_used"] is False
        assert data["pending_clarification_id"] == pending_id
        _assert_no_execution(data)


def test_alpha31D_clarification_answers_and_cancels_still_work() -> None:
    client = _client()

    cid = "alpha31D_answer"
    _open_pending(client, cid)
    answer = _post(client, cid, "answer_a", "A")
    assert answer["route"] == "clarification_resolved"
    assert answer["blocked"] is False
    assert answer["pending_clarification_id"] is None

    cid = "alpha31D_cancel"
    _open_pending(client, cid)
    cancel = _post(client, cid, "cancel", "cancel")
    assert cancel["route"] == "clarification_cancelled"
    assert cancel["blocked"] is False
    assert cancel["pending_clarification_id"] is None

    cid = "alpha31D_cancel_task"
    _open_pending(client, cid)
    cancel_task = _post(client, cid, "cancel_task", "cancel task")
    assert cancel_task["route"] == "active_task_cancelled"
    assert cancel_task["active_task_id"] is None

    cid = "alpha31D_start_new"
    _open_pending(client, cid)
    start_new = _post(client, cid, "start_new", "start new")
    assert start_new["route"] == "active_task_start_new"
    assert start_new["active_task_id"] is None


def test_alpha31D_run_builder_is_not_global_action_outside_pending() -> None:
    client = _client()
    cid = "alpha31D_non_pending_run"
    _start_builder(client, cid)
    data = _post(client, cid, "run_builder_non_pending", "Run builder now")
    assert data["route"] != "clarification_blocked_action"
    assert data["router_step"] != "pending_clarification_gate"
    assert data.get("workbook_read") in (False, None)
    assert data.get("engine_called") in (False, None)
    assert data.get("excel_created") in (False, None)
    assert data.get("legacy_builder_called") in (False, None)
