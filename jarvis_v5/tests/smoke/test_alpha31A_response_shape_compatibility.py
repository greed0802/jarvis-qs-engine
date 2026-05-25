from __future__ import annotations

from fastapi.testclient import TestClient

from jarvis_v5.app import app, _apply_chat_response_shape_compatibility
from jarvis_v5.config import APP_VERSION


def _client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, cid: str, event: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    ).json()


def test_alpha31B_version_and_scope() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["scope"] == "workbook_read_policy_review_no_content_read"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha31B_plan_aliases_no_active_and_active_keep_old_keys() -> None:
    client = _client()
    no_active = client.get("/api/plan/alpha31B_missing_conversation").json()
    assert no_active["version"] == APP_VERSION
    assert no_active["latest_snapshot"] == no_active["snapshot"] == {"found": False}
    assert no_active["latest_adapter"] == no_active["adapter_dry_run"] == {"found": False}
    assert no_active["latest_engine_contract"] == no_active["engine_contract"] == {"found": False}

    cid = "alpha31B_plan_alias_active"
    start = _chat(client, cid, "start", "Build me a BOQ")
    assert start["route"] == "new_builder_task_shell"
    plan = client.get(f"/api/plan/{cid}").json()
    assert plan["version"] == APP_VERSION
    assert plan["latest_snapshot"] == plan["snapshot"]
    assert plan["latest_adapter"] == plan["adapter_dry_run"]
    assert plan["latest_engine_contract"] == plan["engine_contract"]
    assert plan["workbook_read"] is False if "workbook_read" in plan else True


def test_alpha31B_preview_policy_workbook_read_enabled_alias() -> None:
    client = _client()
    data = client.post(
        "/api/builder/preview-execution-policy",
        json={"conversation_id": "alpha31B_preview_policy", "client_event_id": "policy"},
    ).json()
    boundary = data["workbook_read_permission_boundary"]
    assert boundary["enabled"] is False
    assert boundary["workbook_read_enabled"] is False
    assert data["metadata_only"] is True
    assert data["execution_enabled"] is False
    assert data["workbook_read"] is False
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False


def test_alpha31B_plan_mutated_false_for_no_mutation_and_true_for_slot_edit() -> None:
    client = _client()
    no_mutation = _chat(client, "alpha31B_no_mutation", "hello", "Hello Jarvis")
    assert no_mutation["plan_mutated"] is False

    cid = "alpha31B_slot_mutation"
    start = _chat(client, cid, "start", "Build me a BOQ")
    assert start["route"] == "new_builder_task_shell"
    assert start["plan_mutated"] is False
    edit = _chat(client, cid, "trade", "Use Wall Types")
    assert edit["route"] == "active_task_slot_edit"
    assert edit["reducer_result"]["plan_mutated"] is True
    assert edit["plan_mutated"] is True


def test_alpha31B_plan_mutated_helper_preserves_truth_and_changed_slots() -> None:
    assert _apply_chat_response_shape_compatibility({"plan_mutated": True})["plan_mutated"] is True
    assert _apply_chat_response_shape_compatibility({"plan_mutated": False})["plan_mutated"] is False
    assert _apply_chat_response_shape_compatibility({"reducer_result": {"plan_mutated": True}})["plan_mutated"] is True
    assert _apply_chat_response_shape_compatibility({"reducer_result": {"plan_mutated": False}})["plan_mutated"] is False
    assert _apply_chat_response_shape_compatibility({"reducer_result": {"changed_slots": ["trade_profile"]}})["plan_mutated"] is True
    assert _apply_chat_response_shape_compatibility({"reducer_result": {"changed_slots": []}})["plan_mutated"] is False
    assert _apply_chat_response_shape_compatibility({})["plan_mutated"] is False
