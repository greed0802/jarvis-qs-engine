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


def _complete_contract_ready_flow(client: TestClient, conversation_id: str) -> None:
    assert _chat(client, conversation_id, f"{conversation_id}_start", "Build me a BOQ")["route"] == "new_builder_task_shell"
    with open("jarvis_v5/tests/fixtures/Test.xlsx", "rb") as fh:
        attach = client.post(
            "/api/attach",
            data={"conversation_id": conversation_id, "client_event_id": f"{conversation_id}_attach", "text": "Here"},
            files={"file": ("Test.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        ).json()
    assert attach["route"] == "attachment_bind"
    for suffix, text in [
        ("trade", "Use Wall Types"),
        ("function", "Use XGETWALLAREA"),
        ("unit", "Unit m2"),
        ("zone", "Zone 1: Old and New"),
        ("head", "Use Head 2 for Zone 1"),
        ("levels", "Levels GF to L3"),
    ]:
        data = _chat(client, conversation_id, f"{conversation_id}_{suffix}", text)
        assert data["route"] == "active_task_slot_edit"
    snapshot = client.post(
        "/api/builder/create-snapshot",
        json={"conversation_id": conversation_id, "client_event_id": f"{conversation_id}_snapshot"},
    ).json()
    assert snapshot["route"] == "builder_snapshot_created"
    adapter = client.post(
        "/api/builder/adapter-dry-run",
        json={"conversation_id": conversation_id, "client_event_id": f"{conversation_id}_adapter"},
    ).json()
    assert adapter["route"] == "builder_adapter_dry_run"
    contract = client.post(
        "/api/builder/engine-contract",
        json={"conversation_id": conversation_id, "client_event_id": f"{conversation_id}_contract"},
    ).json()
    assert contract["route"] == "builder_engine_contract_created"


def _assert_policy_reviewed_readiness(readiness: dict) -> None:
    assert readiness["status"] == "contract_ready"
    assert readiness["workbook_read_policy_status"] == "reviewed"
    assert readiness["workbook_read_policy_reviewed"] is True
    policy = readiness["workbook_read_policy"]
    assert policy["found"] is True
    assert policy["status"] == "reviewed"
    assert policy["policy_only"] is True
    assert policy["workbook_opened"] is False
    assert policy["workbook_read"] is False
    assert policy["workbook_content_read"] is False
    assert policy["cells_read"] is False
    assert policy["formulas_read"] is False
    assert policy["engine_called"] is False
    assert policy["excel_created"] is False
    assert policy["legacy_builder_called"] is False
    assert readiness["safety"]["workbook_read"] is False
    assert readiness["safety"]["engine_called"] is False
    assert readiness["safety"]["excel_created"] is False
    assert readiness["safety"]["legacy_builder_called"] is False


def test_alpha35_8_version_lock() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha35_8_policy_review_visible_in_plan_without_status_override() -> None:
    client = _client()
    conv = f"alpha35_8_plan_{uuid4().hex}"
    _complete_contract_ready_flow(client, conv)
    before = client.get(f"/api/plan/{conv}").json()
    assert before["readiness"]["status"] == "contract_ready"
    assert before["readiness"]["workbook_read_policy_status"] == "not_reviewed"
    assert before["readiness"]["workbook_read_policy_reviewed"] is False
    policy = client.post(
        "/api/builder/workbook-read-policy-review",
        json={"conversation_id": conv, "client_event_id": f"{conv}_policy"},
    ).json()
    assert policy["route"] == "builder_workbook_read_policy_review"
    assert policy["workbook_read"] is False
    plan = client.get(f"/api/plan/{conv}").json()
    assert plan["workbook_read_policy"]["found"] is True
    assert plan["workbook_read_policy"]["status"] == "reviewed"
    assert plan["workbook_read_policy"]["workbook_read"] is False
    _assert_policy_reviewed_readiness(plan["readiness"])


def test_alpha35_8_policy_review_visible_in_preview_and_export_readiness() -> None:
    client = _client()
    conv = f"alpha35_8_action_{uuid4().hex}"
    _complete_contract_ready_flow(client, conv)
    policy = client.post(
        "/api/builder/workbook-read-policy-review",
        json={"conversation_id": conv, "client_event_id": f"{conv}_policy"},
    ).json()
    assert policy["route"] == "builder_workbook_read_policy_review"
    preview = _chat(client, conv, f"{conv}_preview", "Preview")
    assert preview["route"] == "active_task_preview_stub"
    assert preview["blocked"] is True
    _assert_policy_reviewed_readiness(preview["readiness"])
    export = _chat(client, conv, f"{conv}_export", "Export")
    assert export["route"] == "active_task_export_stub"
    assert export["blocked"] is True
    _assert_policy_reviewed_readiness(export["readiness"])


def test_alpha35_8_no_policy_review_shows_not_reviewed() -> None:
    client = _client()
    conv = f"alpha35_8_not_reviewed_{uuid4().hex}"
    _complete_contract_ready_flow(client, conv)
    plan = client.get(f"/api/plan/{conv}").json()
    assert plan["readiness"]["status"] == "contract_ready"
    assert plan["workbook_read_policy"]["found"] is False
    assert plan["workbook_read_policy"]["status"] == "not_reviewed"
    assert plan["readiness"]["workbook_read_policy_status"] == "not_reviewed"
    assert plan["readiness"]["workbook_read_policy_reviewed"] is False
    assert plan["readiness"]["workbook_read_policy"]["workbook_read"] is False
