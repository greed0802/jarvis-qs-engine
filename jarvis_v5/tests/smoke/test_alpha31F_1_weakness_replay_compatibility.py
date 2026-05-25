from __future__ import annotations

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


def _chat(client: TestClient, cid: str, event: str, text: str) -> dict:
    return client.post(
        "/api/chat",
        json={"conversation_id": cid, "client_event_id": event, "text": text},
    ).json()


def _start_builder(client: TestClient, cid: str) -> None:
    data = _chat(client, cid, f"{cid}_start", "Build me a BOQ")
    assert data["route"] == "new_builder_task_shell"


def _assert_action_diag(data: dict, expected_route: str, expected_action: str) -> None:
    assert data["route"] == expected_route
    assert data["fallback_used"] is False
    assert data.get("plan_mutated") is False
    assert data.get("workbook_read") in (False, None)
    assert data.get("engine_called") in (False, None)
    assert data.get("excel_created") in (False, None)
    assert data.get("legacy_builder_called") in (False, None)
    diag = data.get("active_task_action_language")
    assert isinstance(diag, dict)
    assert diag.get("matched") is True
    assert diag.get("action") == expected_action
    assert diag.get("route_hint") == expected_route


def test_alpha32A_version_and_scope_metadata() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["scope"] == "workbook_read_policy_review_no_content_read"
    assert data["scope_metadata"]["weakness_replay_compatibility_cleanup"] is True
    assert data["scope_metadata"]["active_action_diagnostic_alias"] is True
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha32A_exact_and_natural_active_actions_expose_diagnostics_without_route_change() -> None:
    client = _client()
    cases = [
        ("Review the current setup", "active_task_review", "review"),
        ("Show me the builder plan details", "active_task_review", "review"),
        ("Before preview, review the setup", "active_task_review", "review"),
        ("Preview it please", "active_task_preview_stub", "preview"),
        ("Export current builder output", "active_task_export_stub", "export"),
        ("Download output link", "active_task_action_stub", "download"),
    ]
    for idx, (phrase, expected_route, expected_action) in enumerate(cases):
        cid = f"alpha32A_action_diag_{idx}"
        _start_builder(client, cid)
        data = _chat(client, cid, f"action_{idx}", phrase)
        _assert_action_diag(data, expected_route, expected_action)


def test_alpha32A_exact_alias_uses_exact_reason_but_natural_aliases_preserved() -> None:
    client = _client()

    cid = "alpha32A_exact_review"
    _start_builder(client, cid)
    exact = _chat(client, cid, "exact_review", "Current setup")
    _assert_action_diag(exact, "active_task_review", "review")
    assert exact["active_task_action_language"]["reason"] == "active_task_exact_action_alias"
    assert exact["active_task_action_language"]["alias"] == "exact_review"

    cid = "alpha32A_natural_preview"
    _start_builder(client, cid)
    natural = _chat(client, cid, "natural_preview", "Preview it please")
    _assert_action_diag(natural, "active_task_preview_stub", "preview")
    assert natural["active_task_action_language"]["reason"] == "active_task_action_language:preview"
    assert natural["active_task_action_language"]["alias"] == "natural_preview"
