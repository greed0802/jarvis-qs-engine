from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "jarvis_v5" / "docs"
REGISTRY = ROOT / "jarvis_v5" / "registry"
FUTURE_RUNTIME_DIR = ROOT / "jarvis_v5" / "tools" / "workbook_metadata_probe"
PROTECTED_SAFE_PATH = ROOT / "jarvis_v5" / "tools" / "builder" / "safe_workbook_path_resolver.py"


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


def test_alpha36_3_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_alpha36_3_is_plan_only_no_probe_runtime() -> None:
    assert not FUTURE_RUNTIME_DIR.exists(), "alpha36.3 must not add workbook metadata probe runtime"
    assert PROTECTED_SAFE_PATH.exists(), "protected safe path resolver should remain present but untouched"


def test_alpha36_3_docs_exist_and_are_future_only() -> None:
    required = [
        "ALPHA_36_3_SCOPE.md",
        "SHEET_NAME_PROBE_IMPLEMENTATION_BLUEPRINT.md",
        "SHEET_NAME_PROBE_PERMISSION_SEQUENCE.md",
        "SHEET_NAME_PROBE_NO_CONTENT_ENFORCEMENT_PLAN.md",
        "SHEET_NAME_PROBE_AUDIT_LIFECYCLE.md",
        "SHEET_NAME_PROBE_IMPLEMENTATION_TEST_MATRIX.md",
        "ROADMAP_AFTER_ALPHA_36_2.md",
    ]
    for name in required:
        path = DOCS / name
        assert path.exists(), name
        text = path.read_text().lower()
        assert "alpha36.3" in text or "future" in text or "planning" in text
        assert "no workbook" in text or "workbook_read=false" in text or "does not open" in text or "not executable" in text


def test_alpha36_3_registry_flags_stay_false() -> None:
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


def test_alpha36_3_direct_probe_request_still_safe_blocked() -> None:
    event_id = f"alpha363_direct_probe_block_{uuid4().hex}"
    response = _client().post(
        "/api/chat",
        json={
            "conversation_id": event_id,
            "client_event_id": event_id,
            "text": "Implement and run the sheet-name probe now for this workbook.",
        },
    ).json()
    assert response.get("workbook_read") is not True
    assert response.get("engine_called") is not True
    assert response.get("excel_created") is not True
    assert response.get("legacy_builder_called") is not True
    assert response.get("plan_mutated") is False


def test_alpha36_3_no_runtime_import_markers_in_new_docs() -> None:
    combined = "\n".join((DOCS / name).read_text().lower() for name in [
        "SHEET_NAME_PROBE_IMPLEMENTATION_BLUEPRINT.md",
        "SHEET_NAME_PROBE_PERMISSION_SEQUENCE.md",
        "SHEET_NAME_PROBE_NO_CONTENT_ENFORCEMENT_PLAN.md",
    ])
    assert "import openpyxl" not in combined
    assert "import pandas" not in combined
    assert "load_workbook(" not in combined
    assert "safe_workbook_path_resolver(" not in combined
