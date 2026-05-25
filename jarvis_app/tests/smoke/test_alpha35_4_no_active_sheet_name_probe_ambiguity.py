from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def _client() -> TestClient:
    return TestClient(app)


def _chat(message: str, suffix: str) -> dict:
    response = _client().post(
        "/api/chat",
        json={
            "conversation_id": f"alpha35_6_sheet_probe_{suffix}_{uuid4().hex}",
            "client_event_id": f"evt_{suffix}_{uuid4().hex}",
            "text": message,
        },
    )
    assert response.status_code == 200
    return response.json()


def _assert_no_execution(data: dict) -> None:
    assert data.get("workbook_read") is not True
    assert data.get("workbook_content_read") is not True
    assert data.get("workbook_opened") is not True
    assert data.get("sheet_names_read") is not True
    assert data.get("cells_read") is not True
    assert data.get("formulas_read") is not True
    assert data.get("engine_called") is not True
    assert data.get("excel_created") is not True
    assert data.get("legacy_builder_called") is not True
    safety = data.get("safety") or {}
    assert safety.get("workbook_read") is not True
    assert safety.get("engine_called") is not True
    assert safety.get("excel_created") is not True
    assert safety.get("legacy_builder_called") is not True


def test_alpha35_6_version_lock() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha35_6_no_active_sheet_name_probe_ambiguity_routes_to_choose_tool() -> None:
    cases = [
        "List sheet names after I approve",
        "Show the tabs in this workbook",
        "Sheet names only please",
        "Probe workbook sheets then preview",
        "Open xlsx metadata and sheet names",
        "Use the approved sheet-name probe now",
        "Can you show BOQ tabs?",
        "List Summary BOQ Rates sheets",
        "Read only worksheet names",
        "Open workbook and list sheets",
    ]
    for idx, message in enumerate(cases):
        data = _chat(message, f"sheet_{idx}")
        assert data["route"] == "choose_tool"
        assert data["requires_clarification"] is True
        assert data["fallback_used"] is False
        assert data["route"] != "general_stub"
        assert data["route"] != "new_builder_task_shell"
        no_active = (data.get("route_context") or {}).get("no_active_language") or {}
        assert no_active.get("category") == "sheet_name_probe_ambiguity"
        _assert_no_execution(data)
