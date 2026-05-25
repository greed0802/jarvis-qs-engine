from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.job_contract_schema import JobContractSpec, JobSafetyEnvelope
from jarvis_v5.schemas.output_manifest_schema import OutputManifestSpec


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"


def _client() -> TestClient:
    return TestClient(app)


def _load_registry(name: str) -> dict:
    return json.loads((REGISTRY / name).read_text())


def test_alpha35_15_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_job_contract_schema_defaults_are_no_execution() -> None:
    spec = JobContractSpec(
        job_id="job_contract_only_001",
        job_type="formatter_run",
        source_contract_id="formatter_contract_001",
        source_tool_key="formatter",
    )
    assert spec.metadata_only is True
    assert spec.execution_enabled is False
    assert spec.approval.state == "requires_approval"
    assert spec.progress.state == "draft"
    assert spec.progress.percent == 0
    assert spec.safety.workbook_read is False
    assert spec.safety.engine_called is False
    assert spec.safety.excel_created is False
    assert spec.safety.legacy_builder_called is False
    assert spec.safety.tool_execution_called is False
    assert spec.error_retry.retry_allowed is False
    assert spec.error_retry.max_retries == 0


def test_output_manifest_schema_defaults_are_no_file_creation() -> None:
    manifest = OutputManifestSpec(
        output_id="out_contract_only_001",
        job_id="job_contract_only_001",
        output_type="formatted_workbook",
        source_tool_key="formatter",
    )
    assert manifest.metadata_only is True
    assert manifest.execution_enabled is False
    assert manifest.file_created is False
    assert manifest.file_path_future is None
    assert manifest.download_ref_future is None
    assert manifest.download_policy.download_enabled is False
    assert manifest.download_policy.safe_path_required is True
    assert manifest.retention.cleanup_enabled is False
    assert manifest.safety.workbook_read is False
    assert manifest.safety.engine_called is False
    assert manifest.safety.excel_created is False
    assert manifest.safety.legacy_builder_called is False
    assert manifest.safety.tool_execution_called is False


def test_job_output_registry_metadata_is_disabled() -> None:
    policies = {item["policy_key"]: item for item in _load_registry("execution_policy_registry.json")["policies"]}
    assert "job_output_contract_map" in policies
    assert policies["job_output_contract_map"]["metadata_only"] is True
    assert policies["job_output_contract_map"]["execution_enabled"] is False
    assert "background_worker" in policies["job_output_contract_map"]["blocked"]
    assert "download_route_creation" in policies["job_output_contract_map"]["blocked"]

    capabilities = {item["capability_key"]: item for item in _load_registry("capability_registry.json")["capabilities"]}
    for key in [
        "manage_job_contracts",
        "manage_output_manifests",
        "track_job_progress_contract",
        "record_job_audit_contract",
    ]:
        cap = capabilities[key]
        assert cap["metadata_only"] is True
        assert cap["execution_enabled"] is False
        assert cap["workbook_read_required"] is False
        assert cap["safe_first_mode"] == "contract_advisory_only"

    tools = {item["tool_key"]: item for item in _load_registry("tool_registry.json")["tools"]}
    output_center = tools["output_center"]
    assert output_center["metadata_only"] is True
    assert output_center["execution_enabled"] is False
    assert output_center["workbook_read_required"] is False
    assert "background_worker" in output_center["blocked_in_alpha35_15"]
    assert output_center["safety_policy"]["file_created"] is False
    assert output_center["safety_policy"]["download_enabled"] is False


def test_file_requirement_job_output_placeholders_are_metadata_only() -> None:
    requirements = {item["file_key"]: item for item in _load_registry("file_requirement_registry.json")["file_requirements"]}
    for key in [
        "job_contract_future",
        "output_manifest_future",
        "audit_log_future",
        "download_policy_future",
        "retention_policy_future",
    ]:
        item = requirements[key]
        assert item["metadata_only"] is True
        assert item["execution_enabled"] is False
        assert item["real_file_required"] is False


def test_future_tool_requests_still_metadata_only_no_execution() -> None:
    payload = _client().post(
        "/api/chat",
        json={
            "conversation_id": "alpha3515_run_formatter",
            "client_event_id": "alpha3515_run_formatter",
            "text": "Run Formatter on the Builder output",
        },
    ).json()
    assert payload["route"] == "registry_advisory_metadata_only"
    assert payload["metadata_only"] is True
    assert payload["execution_enabled"] is False
    assert payload["workbook_read"] is False
    assert payload["engine_called"] is False
    assert payload["excel_created"] is False
    assert payload["legacy_builder_called"] is False
    advisor = payload["requirement_advisor"]
    assert advisor["execution_blocked"] is True
    assert advisor["tool_execution_called"] is False
