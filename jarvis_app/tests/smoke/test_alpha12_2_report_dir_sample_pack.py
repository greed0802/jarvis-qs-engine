from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import TEST_REPORTS_DIR
from jarvis_v5.qa_runner.test_executor import TestPackExecutor
from jarvis_v5.tests.smoke.test_cleanup import safe_rmtree


def test_alpha12_2_report_directory_is_recreated_for_write_report():
    if TEST_REPORTS_DIR.exists():
        safe_rmtree(TEST_REPORTS_DIR)
    assert not TEST_REPORTS_DIR.exists()

    result = TestPackExecutor(app, write_report=True).run_pack("sample_external_ai_pack_valid")

    assert result["overall"] == "PASS", result.get("failures")
    assert result["failed"] == 0
    assert TEST_REPORTS_DIR.exists()
    assert Path(result["report_json"]).exists()
    assert Path(result["report_md"]).exists()
    assert result["safety"]["workbook_read_any_true"] is False
    assert result["safety"]["engine_called_any_true"] is False
    assert result["safety"]["excel_created_any_true"] is False
    assert result["safety"]["legacy_builder_called_any_true"] is False


def test_alpha12_2_dev_endpoint_write_report_true_recreates_directory():
    if TEST_REPORTS_DIR.exists():
        safe_rmtree(TEST_REPORTS_DIR)
    client = TestClient(app)
    response = client.post("/api/dev/run-smoke-tests", json={"pack": "sample_external_ai_pack_valid", "write_report": True})

    assert response.status_code == 200
    data = response.json()
    assert data["overall"] == "PASS", data.get("failures")
    assert data["failed"] == 0
    assert Path(data["report_json"]).exists()
    assert Path(data["report_md"]).exists()


def test_alpha12_2_sample_external_pack_no_report_passes():
    result = TestPackExecutor(app, write_report=False).run_pack("sample_external_ai_pack_valid")
    assert result["overall"] == "PASS", result.get("failures")
    assert result["passed"] == 1
    assert result["failed"] == 0


def test_alpha12_2_builtin_pack_write_report_passes():
    result = TestPackExecutor(app, write_report=True).run_pack("alpha11_contract_negative_guards")
    assert result["overall"] == "PASS", result.get("failures")
    assert result["failed"] == 0
    assert Path(result["report_json"]).exists()
    assert Path(result["report_md"]).exists()


def test_alpha12_2_validate_sample_pack_has_no_warnings():
    loaded_result = TestPackExecutor(app, write_report=False).run_pack("sample_external_ai_pack_valid")
    assert loaded_result["overall"] == "PASS"
    assert loaded_result["preflight"]["errors"] == []
    assert loaded_result["preflight"]["warnings"] == []


def test_alpha12_2_report_write_error_is_structured(monkeypatch):
    import jarvis_v5.qa_runner.test_executor as executor_module

    def boom(_result, _pack_name):
        raise OSError("simulated write failure")

    monkeypatch.setattr(executor_module, "write_reports", boom)
    result = TestPackExecutor(app, write_report=True).run_pack("sample_external_ai_pack_valid")

    assert result["overall"] == "FAIL"
    assert result["error_type"] == "report_write_error"
    assert result["report_json"] is None
    assert result["report_md"] is None
    assert result["safety"]["engine_called_any_true"] is False


def test_alpha12_2_missing_fixture_still_fails_cleanly(tmp_path: Path):
    pack = tmp_path / "missing_fixture.json"
    pack.write_text(json.dumps({
        "pack_name": "missing_fixture_alpha12_2",
        "tests": [{
            "name": "missing_fixture_case",
            "steps": [{
                "name": "attach_missing_fixture",
                "method": "POST",
                "endpoint": "/api/attach",
                "form": {"conversation_id": "missing_fixture_12_2", "client_event_id": "missing_fixture_12_2_evt", "text": "Here"},
                "file_fixture": "Missing.xlsx",
                "assertions": [{"path": "$.route", "equals": "attachment_bind"}]
            }]
        }]
    }), encoding="utf-8")

    result = TestPackExecutor(app, write_report=False).run_pack(str(pack))
    assert result["overall"] == "FAIL"
    assert result["tests"][0]["steps"][0]["response_json"]["error_type"] == "fixture_not_found"
    assert result["safety"]["engine_called_any_true"] is False
