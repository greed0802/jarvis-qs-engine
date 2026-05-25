from __future__ import annotations

import ast
import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.workbook_metadata_probe_contract_schema import (
    SheetNameOnlyProbeOutputContract,
    WorkbookMetadataProbeBlockedResult,
    WorkbookMetadataProbePlanResponse,
    WorkbookMetadataProbeSafetyEnvelope,
)

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"
DOCS = ROOT / "jarvis_v5" / "docs"
SCHEMA = ROOT / "jarvis_v5" / "schemas" / "workbook_metadata_probe_contract_schema.py"
FUTURE_RUNTIME_DIR = ROOT / "jarvis_v5" / "tools" / "workbook_metadata_probe"


def _client() -> TestClient:
    return TestClient(app)


def _walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_alpha36_2_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha36_2_remains_dry_run_no_probe_runtime() -> None:
    assert not FUTURE_RUNTIME_DIR.exists(), "alpha36.2 must not create workbook metadata probe runtime"
    safety = WorkbookMetadataProbeSafetyEnvelope()
    assert safety.metadata_only is True
    assert safety.execution_enabled is False
    assert safety.workbook_read is False
    assert safety.workbook_content_read is False
    assert safety.sheet_name_probe_allowed is False
    assert safety.formula_read is False
    assert safety.cell_value_read is False
    assert safety.style_read is False

    response = WorkbookMetadataProbePlanResponse(version=APP_VERSION)
    assert response.sheet_name_probe_allowed is False
    assert response.workbook_read is False
    assert response.workbook_content_read is False
    assert response.formula_read is False
    assert response.cell_value_read is False
    assert response.style_read is False


def test_alpha36_2_future_output_and_blocked_result_are_not_real_probe_results() -> None:
    output = SheetNameOnlyProbeOutputContract()
    assert output.status == "future_only_not_enabled"
    assert output.sheet_names == []
    assert output.sheet_count is None
    assert output.workbook_read is False
    assert output.formula_read is False
    assert output.cell_value_read is False
    assert output.style_read is False

    blocked = WorkbookMetadataProbeBlockedResult()
    assert blocked.status == "blocked"
    assert blocked.sheet_names == []
    assert blocked.sheet_name_probe_allowed is False
    assert blocked.workbook_read is False
    assert blocked.formula_read is False
    assert blocked.cell_value_read is False


def test_alpha36_2_registry_flags_stay_false() -> None:
    bad_true_keys = {
        "execution_enabled",
        "workbook_read",
        "workbook_content_read",
        "sheet_name_probe_allowed",
        "formula_read",
        "cell_value_read",
        "style_read",
        "engine_called",
        "excel_created",
        "legacy_builder_called",
        "tool_execution_called",
    }
    for path in sorted(REGISTRY.glob("*.json")):
        data = json.loads(path.read_text())
        for item in _walk(data):
            for key in bad_true_keys:
                if key in item:
                    assert item[key] is not True, f"{path} has {key}=true in {item}"


def test_alpha36_2_schema_has_no_workbook_read_imports() -> None:
    tree = ast.parse(SCHEMA.read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    banned = {
        "openpyxl",
        "pandas",
        "xlrd",
        "pyxlsb",
        "jarvis_v5.tools.builder.safe_workbook_path_resolver",
    }
    assert not (set(imports) & banned)
    text = SCHEMA.read_text()
    assert "load_workbook" not in text
    assert "safe_workbook_path_resolver" not in text


def test_alpha36_2_direct_probe_request_still_safe_blocked() -> None:
    event_id = f"alpha362_direct_probe_block_{uuid4().hex}"
    response = _client().post(
        "/api/chat",
        json={
            "conversation_id": event_id,
            "client_event_id": event_id,
            "text": "Probe this workbook and list the sheet names now, but do not read cells.",
        },
    ).json()
    assert response.get("workbook_read") is not True
    assert response.get("engine_called") is not True
    assert response.get("excel_created") is not True
    assert response.get("legacy_builder_called") is not True
    assert response.get("plan_mutated") is False
    registry_assist = response.get("registry_assist") or {}
    assert registry_assist.get("execution_enabled") is False
    assert registry_assist.get("metadata_only") is True


def test_alpha36_2_docs_exist_and_state_no_implementation() -> None:
    for name in [
        "ALPHA_36_2_SCOPE.md",
        "SHEET_NAME_PROBE_DRY_RUN_PATCH_MAP.md",
        "SHEET_NAME_PROBE_FUTURE_BOUNDARY_REVIEW.md",
        "SHEET_NAME_PROBE_NO_READ_SAFETY_REVIEW.md",
        "ROADMAP_AFTER_ALPHA_36_1.md",
    ]:
        path = DOCS / name
        assert path.exists(), name
        text = path.read_text().lower()
        assert (
            "no workbook" in text
            or "workbook_read=false" in text
            or "does not open" in text
            or "no runtime" in text
            or "no-touch" in text
        )
