from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.qa_runner.test_executor import TestPackExecutor
from jarvis_v5.qa_runner.test_pack_loader import load_test_pack


def test_alpha12_builtin_pack_loads():
    pack = load_test_pack("alpha11_contract_negative_guards")
    assert pack.pack_name == "alpha11_contract_negative_guards"
    assert len(pack.tests) >= 7


def test_alpha12_runner_executes_builtin_pack_without_engine():
    with TestPackExecutor(app, write_report=False) as executor:
        result = executor.run_pack("alpha11_contract_negative_guards")
    assert result["overall"] == "PASS", result.get("failures")
    assert result["failed"] == 0
    assert result["safety"]["workbook_read_any_true"] is False
    assert result["safety"]["engine_called_any_true"] is False
    assert result["safety"]["excel_created_any_true"] is False
    assert result["safety"]["legacy_builder_called_any_true"] is False


def test_alpha12_dev_endpoint_runs_pack_and_returns_summary():
    client = TestClient(app)
    response = client.post("/api/dev/run-smoke-tests", json={"pack": "alpha11_contract_negative_guards", "write_report": False})
    assert response.status_code == 200
    data = response.json()
    assert data["route"] == "dev_smoke_tests_completed"
    assert data["overall"] == "PASS", data.get("failures")
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False


def test_alpha12_importable_custom_pack(tmp_path: Path):
    custom_pack = tmp_path / "custom_pack.json"
    custom_pack.write_text(json.dumps({
        "pack_name": "custom_pack",
        "version_target": APP_VERSION,
        "tests": [
            {
                "name": "version_check",
                "steps": [
                    {
                        "name": "version",
                        "method": "GET",
                        "endpoint": "/api/version",
                        "assertions": [
                            {"path": "$.version", "equals": APP_VERSION},
                            {"path": "$.engines_connected.builder", "equals": False}
                        ]
                    }
                ]
            }
        ]
    }), encoding="utf-8")
    with TestPackExecutor(app, write_report=False) as executor:
        result = executor.run_pack(str(custom_pack))
    assert result["overall"] == "PASS", result.get("failures")
