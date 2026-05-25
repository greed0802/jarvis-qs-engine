from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.qa_runner.test_executor import TestPackExecutor


def test_alpha12_1_version():
    assert APP_VERSION.startswith("v5.0.0-alpha.")


def test_alpha12_1_builtin_pack_still_passes():
    result = TestPackExecutor(app, write_report=False).run_pack("alpha11_contract_negative_guards")
    assert result["overall"] == "PASS", result.get("failures")
    assert result["safety"]["workbook_read_any_true"] is False
    assert result["safety"]["engine_called_any_true"] is False
    assert result["safety"]["excel_created_any_true"] is False
    assert result["safety"]["legacy_builder_called_any_true"] is False


def test_alpha12_1_sample_external_pack_with_fixture_passes():
    result = TestPackExecutor(app, write_report=False).run_pack("sample_external_ai_pack_valid")
    assert result["overall"] == "PASS", result.get("failures")
    assert result["failed"] == 0


def test_alpha12_1_bad_json_returns_invalid_pack(tmp_path: Path):
    bad = tmp_path / "bad_pack.json"
    bad.write_text('{"pack_name":"bad","tests":[{"name":"oops"', encoding="utf-8")
    result = TestPackExecutor(app, write_report=False).run_pack(str(bad))
    assert result["overall"] == "INVALID_PACK"
    assert result["error_type"] == "json_parse_error"
    assert result["engine_called"] is False


def test_alpha12_1_dev_endpoint_bad_json_returns_422(tmp_path: Path):
    bad = tmp_path / "bad_pack.json"
    bad.write_text('{"pack_name":"bad","tests":[', encoding="utf-8")
    client = TestClient(app)
    response = client.post("/api/dev/run-smoke-tests", json={"pack": str(bad), "write_report": False})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["overall"] == "INVALID_PACK"
    assert detail["error_type"] == "json_parse_error"
    assert detail["engine_called"] is False


def test_alpha12_1_fixture_missing_is_clean_step_failure(tmp_path: Path):
    pack = tmp_path / "missing_fixture.json"
    pack.write_text(json.dumps({
        "pack_name": "missing_fixture",
        "tests": [
            {
                "name": "missing_fixture_case",
                "steps": [
                    {
                        "name": "attach_missing_fixture",
                        "method": "POST",
                        "endpoint": "/api/attach",
                        "form": {"conversation_id": "missing_fixture_conv", "client_event_id": "missing_fixture_evt", "text": "Here"},
                        "file_fixture": "Missing.xlsx",
                        "assertions": [{"path": "$.route", "equals": "attachment_bind"}]
                    }
                ]
            }
        ]
    }), encoding="utf-8")
    result = TestPackExecutor(app, write_report=False).run_pack(str(pack))
    assert result["overall"] == "FAIL"
    step = result["tests"][0]["steps"][0]
    assert step["response_json"]["error_type"] == "fixture_not_found"
    assert step["response_json"]["engine_called"] is False


def test_alpha12_1_validate_endpoint_warns_on_bad_ai_pack(tmp_path: Path):
    pack = tmp_path / "bad_ai_expectations.json"
    pack.write_text(json.dumps({
        "pack_name": "bad_ai_expectations",
        "tests": [
            {
                "name": "bad_route_and_attach",
                "steps": [
                    {
                        "name": "attach_wrong",
                        "method": "POST",
                        "endpoint": "/api/attach",
                        "json": {"conversation_id": "bad_ai", "client_event_id": "bad_ai_attach", "file": "Test.xlsx"},
                        "assertions": [{"path": "$.route", "equals": "made_up_route"}]
                    }
                ]
            }
        ]
    }), encoding="utf-8")
    client = TestClient(app)
    response = client.post("/api/dev/validate-test-pack", json={"pack": str(pack)})
    assert response.status_code == 200
    data = response.json()
    warning_types = {item["type"] for item in data["warnings"]}
    assert "attach_json_file_not_supported" in warning_types
    assert "unknown_expected_route" in warning_types


def test_alpha12_1_path_not_found_has_fields_and_hint(tmp_path: Path):
    pack = tmp_path / "missing_path.json"
    pack.write_text(json.dumps({
        "pack_name": "missing_path",
        "tests": [
            {
                "name": "missing_path_case",
                "steps": [
                    {
                        "name": "version",
                        "method": "GET",
                        "endpoint": "/api/version",
                        "assertions": [{"path": "$.does_not_exist", "equals": False}]
                    }
                ]
            }
        ]
    }), encoding="utf-8")
    result = TestPackExecutor(app, write_report=False).run_pack(str(pack))
    failure = result["tests"][0]["steps"][0]["failures"][0]
    assert failure["error_type"] == "path_not_found"
    assert "available_top_level_fields" in failure
    assert "hint" in failure
