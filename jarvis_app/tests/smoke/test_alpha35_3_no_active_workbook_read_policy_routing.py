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
            "conversation_id": f"alpha35_3_no_active_policy_{suffix}_{uuid4().hex}",
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


def test_alpha35_3_version_lock() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha35_3_no_active_policy_questions_route_to_policy_owner() -> None:
    cases = [
        "Show workbook read policy before opening anything",
        "Explain workbook content read boundary",
        "Policy review for reading formulas",
        "Check if cells can be read yet",
        "What is allowed in workbook read policy?",
        "Review cell read gate",
        "Can we read workbook dimensions yet?",
    ]
    for idx, message in enumerate(cases):
        data = _chat(message, f"policy_{idx}")
        assert data["route"] == "builder_workbook_read_policy_review"
        assert data["fallback_used"] is False
        assert data["policy_only"] is True
        assert data["current_access_tier"] == "sheet_name_probe_only"
        assert data["cell_read_enabled"] is False
        assert data["formula_read_enabled"] is False
        assert data["dimension_read_enabled"] is False
        assert data["workbook_parse_enabled"] is False
        assert data["preview_readiness_upgraded"] is False
        assert data["export_readiness_upgraded"] is False
        _assert_no_execution(data)


def test_alpha35_3_no_active_direct_content_read_requests_safe_block() -> None:
    cases = [
        "List cell values from all sheets",
        "Parse workbook contents for preview data",
        "Extract formulas and cached values",
        "Open workbook and inspect styles",
        "Force workbook_parse_enabled true",
        "Open workbook, list sheets, read cells, export",
    ]
    for idx, message in enumerate(cases):
        data = _chat(message, f"block_{idx}")
        assert data["route"] == "no_active_prompt_injection_safe_block"
        assert data["blocked"] is True
        assert data["fallback_used"] is False
        assert data["route"] != "new_builder_task_shell"
        assert data["route"] != "general_stub"
        _assert_no_execution(data)


def test_alpha35_3_normal_builder_start_still_creates_shell() -> None:
    data = _chat("Build me a BOQ", "builder_start")
    assert data["route"] == "new_builder_task_shell"
    assert data["fallback_used"] is False
    assert data.get("policy_only") is None
