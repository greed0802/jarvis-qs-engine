from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION, PACKAGE_ROOT
from jarvis_v5.parsers.conflict_guard import detect_setup_conflict
from jarvis_v5.parsers.level_parser import parse_levels


def _client() -> TestClient:
    return TestClient(app)


def _chat(client: TestClient, conversation_id: str, event_id: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "text": text},
    ).json()


def _attach_fixture(client: TestClient, conversation_id: str, event_id: str = "attach") -> dict:
    with open(PACKAGE_ROOT / "tests" / "fixtures" / "Test.xlsx", "rb") as fh:
        return client.post(
            "/api/attach",
            data={"conversation_id": conversation_id, "client_event_id": event_id, "text": "Here"},
            files={"file": ("Test.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
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


def _complete_uae_setup(client: TestClient, conversation_id: str) -> dict:
    assert _chat(client, conversation_id, f"{conversation_id}_start", "Build me a BOQ")["route"] == "new_builder_task_shell"
    attach = _attach_fixture(client, conversation_id, f"{conversation_id}_attach")
    assert attach["route"] == "attachment_bind"
    assert attach["reducer_result"]["workbook_read"] is False

    for suffix, text in [
        ("trade", "Use Wall Types"),
        ("function_unit", "Use XGETWALLAREA unit m2"),
        ("zone", "Zone 1: Old and New"),
        ("head", "Use Head 2 for Zone 1"),
    ]:
        assert _chat(client, conversation_id, f"{conversation_id}_{suffix}", text)["route"] == "active_task_slot_edit"

    return _chat(
        client,
        conversation_id,
        f"{conversation_id}_levels",
        "Levels B3 to B1, GF, Podium, Level 1 to Level 20",
    )


def test_alpha35_10_1_version_lock() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_uae_podium_descending_basement_levels_parse_without_clarification() -> None:
    parsed = parse_levels("Levels B3 to B1, GF, Podium, Level 1 to Level 20")
    assert parsed is not None
    for level in ["B3", "B2", "B1", "GF", "Podium", "L1", "L20"]:
        assert level in parsed["levels"]
    assert detect_setup_conflict({}, "Levels B3 to B1, GF, Podium, Level 1 to Level 20") is None


def test_ascending_basement_range_still_requires_clarification() -> None:
    conflict = detect_setup_conflict({}, "Levels B2 to B5")
    assert conflict is not None
    assert conflict["conflict_type"] == "ambiguous_basement_range"
    assert conflict["conflicting_slots"] == ["levels"]


def test_uae_podium_basement_flow_reaches_snapshot_and_adapter_without_engine() -> None:
    client = _client()
    conversation_id = f"alpha35_10_1_uae_{uuid4().hex}"

    levels = _complete_uae_setup(client, conversation_id)
    assert levels["route"] == "active_task_slot_edit"
    assert levels["pending_clarification_id"] is None
    assert levels["reducer_result"]["requires_clarification"] is False
    assert levels["reducer_result"]["conflicts"] == []
    for level in ["B3", "B2", "B1", "GF", "Podium", "L1", "L20"]:
        assert level in levels["reducer_result"]["changes"]["levels"]

    review = _chat(client, conversation_id, f"{conversation_id}_review", "Review")
    assert review["route"] == "active_task_review"
    assert review["readiness"]["safety"]["workbook_read"] is False
    assert review["readiness"]["safety"]["engine_called"] is False
    assert review["readiness"]["safety"]["excel_created"] is False
    assert review["readiness"]["safety"]["legacy_builder_called"] is False

    snap = client.post(
        "/api/builder/create-snapshot",
        json={"conversation_id": conversation_id, "client_event_id": f"{conversation_id}_snap"},
    ).json()
    assert snap["route"] == "builder_snapshot_created"
    assert snap["blocked"] is False
    _assert_no_engine_safety(snap)

    adapter = client.post(
        "/api/builder/adapter-dry-run",
        json={"conversation_id": conversation_id, "client_event_id": f"{conversation_id}_adapter"},
    ).json()
    assert adapter["route"] == "builder_adapter_dry_run"
    assert adapter["blocked"] is False
    _assert_no_engine_safety(adapter)
