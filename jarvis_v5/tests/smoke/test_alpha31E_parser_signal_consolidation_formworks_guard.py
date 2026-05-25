from __future__ import annotations

from fastapi.testclient import TestClient

from jarvis_v5 import config
from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.tests.smoke.test_cleanup import safe_rmtree
from jarvis_v5.parsers.setup_signal_helpers import (
    detect_custom_quantity_signals,
    detect_function_signals,
    detect_trade_signals,
    detect_unit_signals,
)


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


def _edit(text: str, cid_suffix: str) -> dict:
    client = _client()
    cid = f"alpha31E_{cid_suffix}"
    _start_builder(client, cid)
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": f"{cid}_edit", "text": text},
    ).json()


def _assert_no_execution(data: dict) -> None:
    assert data.get("workbook_read") in (False, None)
    assert data.get("engine_called") in (False, None)
    assert data.get("excel_created") in (False, None)
    assert data.get("legacy_builder_called") in (False, None)


def test_alpha31E_version_and_safety_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["scope"] == "workbook_read_policy_review_no_content_read"
    assert data["scope_metadata"]["parser_signal_helper_owner"] is True
    assert data["scope_metadata"]["formworks_unit_compatibility_guard"] is True
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha31E_shared_signal_helper_detects_expected_signals() -> None:
    text = "Use XGETCUSTOM Formworks unit m2"
    assert detect_function_signals(text) == ["XGETCUSTOM"]
    assert detect_custom_quantity_signals(text) == ["Formworks"]
    assert detect_unit_signals(text, prefer_explicit_units=True) == ["m2"]
    assert detect_trade_signals("Use Structural Steel", include_registry=True) == ["Structural Steel"]


def test_alpha31E_formworks_unit_t_needs_clarification() -> None:
    data = _edit("Use XGETCUSTOM Formworks unit t", "formworks_t")
    assert data["route"] == "active_task_slot_edit_needs_clarification"
    assert data["requires_clarification"] is True
    assert data["plan_mutated"] is False
    assert data.get("reducer_result", {}).get("conflict_type") == "function_unit_conflict"
    _assert_no_execution(data)


def test_alpha31E_formworks_unit_m2_remains_valid() -> None:
    data = _edit("Use XGETCUSTOM Formworks unit m2", "formworks_m2")
    assert data["route"] == "active_task_slot_edit"
    assert data["plan_mutated"] is True
    assert data.get("requires_clarification") is False
    _assert_no_execution(data)


def test_alpha31E_existing_invalid_function_unit_pairs_still_clarify() -> None:
    cases = [
        ("Use Steel Surface Area unit no", "steel_no"),
        ("Use Reinforcement Weight unit m2", "reo_m2"),
        ("Use XGETCOUNT m²", "count_m2"),
        ("Use XGETWALLAREA with unit no", "wall_no"),
        ("Use Count with unit m2", "count_alias_m2"),
    ]
    for text, suffix in cases:
        data = _edit(text, suffix)
        assert data["route"] == "active_task_slot_edit_needs_clarification", text
        assert data["plan_mutated"] is False, text
        _assert_no_execution(data)


def test_alpha31E_existing_valid_setup_edits_still_mutate() -> None:
    cases = [
        ("Use XGETCOUNT unit no", "count_no"),
        ("Use XGETWALLAREA unit m2", "wall_m2"),
        ("Use Reinforcement Weight unit t", "reo_t"),
        ("Use Steel Surface Area unit m2", "steel_m2"),
        ("Use Wall Types", "wall_types"),
        ("Use Structural Steel", "structural_steel"),
    ]
    for text, suffix in cases:
        data = _edit(text, suffix)
        assert data["route"] == "active_task_slot_edit", text
        assert data["plan_mutated"] is True, text
        _assert_no_execution(data)
