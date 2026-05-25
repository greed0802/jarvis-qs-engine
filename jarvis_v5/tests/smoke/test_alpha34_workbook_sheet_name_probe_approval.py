from __future__ import annotations

import ast
import json
import uuid
from pathlib import Path
from zipfile import ZipFile

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION, ATTACHMENTS_DIR
from jarvis_v5.tools.builder.workbook_sheet_name_probe_approval import evaluate_workbook_sheet_name_probe_approval

FORBIDDEN_EXACT_RAW_PATH_KEYS = {
    "saved_path",
    "absolute_path",
    "file_path",
    "local_path",
    "stored_path",
    "resolved_path",
    "raw_path",
    "attachment_path",
    "directory",
    "parent",
    "full_path",
    "path",
}


def _client() -> TestClient:
    return TestClient(app)


def _cid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _chat(client: TestClient, cid: str, event: str, text: str) -> dict:
    return client.post("/api/chat", json={"conversation_id": cid, "client_event_id": event, "text": text}).json()


def _contains_forbidden_exact_key(payload) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_EXACT_RAW_PATH_KEYS:
                return True
            if _contains_forbidden_exact_key(value):
                return True
    if isinstance(payload, list):
        return any(_contains_forbidden_exact_key(item) for item in payload)
    return False


def _ready_contract(client: TestClient, cid: str) -> dict:
    assert _chat(client, cid, "start", "Build me a BOQ")["route"] == "new_builder_task_shell"
    with open("jarvis_v5/tests/fixtures/SheetProbe.xlsx", "rb") as fh:
        attach = client.post(
            "/api/attach",
            data={"conversation_id": cid, "client_event_id": "attach", "text": "Here"},
            files={"file": ("SheetProbe.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        ).json()
    assert attach["route"] == "attachment_bind"
    for event, text in [
        ("trade", "Use Wall Types"),
        ("func", "Use XGETWALLAREA"),
        ("unit", "Unit m2"),
        ("zone", "Zone 1: Old and New"),
        ("head", "Use Head 2 for Zone 1"),
        ("levels", "Levels GF to L3"),
    ]:
        assert _chat(client, cid, event, text)["route"] == "active_task_slot_edit"
    assert client.post("/api/builder/create-snapshot", json={"conversation_id": cid, "client_event_id": "snap"}).json()["route"] == "builder_snapshot_created"
    assert client.post("/api/builder/adapter-dry-run", json={"conversation_id": cid, "client_event_id": "adapter"}).json()["route"] == "builder_adapter_dry_run"
    contract = client.post("/api/builder/engine-contract", json={"conversation_id": cid, "client_event_id": "contract"}).json()
    assert contract["route"] == "builder_engine_contract_created"
    assert contract["contract"]["workbook_ref"]["saved_path"]
    return contract


def _assert_sheet_probe_base_safety(data: dict) -> None:
    assert data["workbook_read"] is False
    assert data["workbook_content_read"] is False
    assert data["workbook_parsed"] is False
    assert data["cells_read"] is False
    assert data["formulas_read"] is False
    assert data["engine_called"] is False
    assert data["excel_created"] is False
    assert data["legacy_builder_called"] is False
    assert data["raw_path_value_returned"] is False
    assert data["forbidden_path_key_returned"] is False
    assert data["preview_readiness_upgraded"] is False
    assert data["export_readiness_upgraded"] is False
    assert data["safety"]["workbook_read"] is False
    assert data["safety"]["workbook_content_read"] is False
    assert data["safety"]["cells_read"] is False
    assert data["safety"]["formulas_read"] is False


def test_alpha34_version_sheet_name_probe_locks() -> None:
    version = _client().get("/api/version").json()
    assert version["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert version["scope"] == "workbook_read_policy_review_no_content_read"
    assert version["scope_metadata"]["workbook_metadata_probe_approval_contract"] is True
    assert version["scope_metadata"]["workbook_sheet_name_probe_approval_contract"] is True
    assert version["scope_metadata"]["workbook_sheet_names_enabled"] is True
    assert version["scope_metadata"]["workbook_parse_enabled"] is False
    assert version["execution_locks"]["workbook_read_enabled"] is False
    assert version["execution_locks"]["builder_engine_execution_enabled"] is False
    assert version["execution_locks"]["legacy_builder_callable"] is False
    assert version["execution_locks"]["excel_output_enabled"] is False


def test_alpha34_no_contract_blocks() -> None:
    data = _client().post(
        "/api/builder/workbook-sheet-name-probe-approval",
        json={"conversation_id": _cid("alpha34_no_contract"), "client_event_id": "probe", "approval_granted": False},
    ).json()
    assert data["route"] == "builder_workbook_sheet_name_probe_approval"
    assert data["blocked"] is True
    assert data["reason"] == "engine_contract_not_found"
    assert data["workbook_opened"] is False
    assert data["workbook_closed"] is False
    assert data["limited_metadata_read"] is False
    assert data["sheet_names_read"] is False
    _assert_sheet_probe_base_safety(data)
    assert _contains_forbidden_exact_key(data) is False


def test_alpha34_no_approval_blocks_ready_contract() -> None:
    client = _client()
    cid = _cid("alpha34_no_approval")
    _ready_contract(client, cid)
    data = client.post(
        "/api/builder/workbook-sheet-name-probe-approval",
        json={"conversation_id": cid, "client_event_id": "probe", "approval_granted": False},
    ).json()
    assert data["blocked"] is True
    assert data["reason"] == "sheet_name_probe_approval_required"
    assert data["approval_required"] is True
    assert data["workbook_opened"] is False
    assert data["sheet_names_read"] is False
    _assert_sheet_probe_base_safety(data)


def test_alpha34_approved_valid_workbook_returns_sheet_names_only_and_closes() -> None:
    client = _client()
    cid = _cid("alpha34_approved")
    contract = _ready_contract(client, cid)
    raw_saved_path = contract["contract"]["workbook_ref"]["saved_path"]
    data = client.post(
        "/api/builder/workbook-sheet-name-probe-approval",
        json={"conversation_id": cid, "client_event_id": "probe", "approval_granted": True},
    ).json()
    assert data["route"] == "builder_workbook_sheet_name_probe_approval"
    assert data["blocked"] is False
    assert data["reason"] == "sheet_name_probe_approved_sheet_names_only"
    assert data["workbook_opened"] is True
    assert data["workbook_closed"] is True
    assert data["limited_metadata_read"] is True
    assert data["sheet_names_read"] is True
    assert data["sheet_names"]
    assert data["sheet_count"] == len(data["sheet_names"])
    _assert_sheet_probe_base_safety(data)
    assert _contains_forbidden_exact_key(data) is False
    assert raw_saved_path not in json.dumps(data, sort_keys=True)


def test_alpha34_missing_workbook_ref_blocks() -> None:
    data = evaluate_workbook_sheet_name_probe_approval(
        conversation_id="alpha34_no_ref",
        client_event_id="direct",
        contract={"contract_id": "contract_fake", "workbook_ref": {}},
        approval_granted=True,
    )
    assert data["blocked"] is True
    assert data["reason"] == "workbook_ref_not_found"
    assert data["workbook_opened"] is False
    assert data["sheet_names_read"] is False
    _assert_sheet_probe_base_safety(data)


def test_alpha34_fake_corrupt_xlsx_blocks_safely() -> None:
    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
    fake = ATTACHMENTS_DIR / f"att_{uuid.uuid4().hex}_Fake.xlsx"
    fake.write_bytes(b"not a workbook")
    data = evaluate_workbook_sheet_name_probe_approval(
        conversation_id="alpha34_fake",
        client_event_id="direct",
        contract={"contract_id": "contract_fake", "workbook_ref": {"filename": "Fake.xlsx", "saved_path": str(fake), "source": "upload"}},
        approval_granted=True,
    )
    assert data["blocked"] is True
    assert data["reason"] == "workbook_sheet_name_probe_failed"
    assert data["workbook_opened"] is False
    assert data["sheet_names_read"] is False
    assert data["workbook_closed"] is False
    _assert_sheet_probe_base_safety(data)
    assert str(fake) not in json.dumps(data, sort_keys=True)


def test_alpha34_unsupported_extension_and_unsafe_path_block_safely() -> None:
    data = evaluate_workbook_sheet_name_probe_approval(
        conversation_id="alpha34_bad_ext",
        contract={"contract_id": "contract_bad", "workbook_ref": {"filename": "Bad.pdf", "saved_path": str(ATTACHMENTS_DIR / "Bad.pdf")}},
        approval_granted=True,
    )
    assert data["blocked"] is True
    assert data["reason"] == "workbook_extension_not_allowed"
    _assert_sheet_probe_base_safety(data)
    unsafe = evaluate_workbook_sheet_name_probe_approval(
        conversation_id="alpha34_unsafe",
        contract={"contract_id": "contract_unsafe", "workbook_ref": {"filename": "Unsafe.xlsx", "saved_path": "/tmp/Unsafe.xlsx"}},
        approval_granted=True,
    )
    assert unsafe["blocked"] is True
    assert unsafe["reason"] == "unsafe_workbook_path"
    _assert_sheet_probe_base_safety(unsafe)
    assert "/tmp/Unsafe.xlsx" not in json.dumps(unsafe, sort_keys=True)


def test_alpha34_alpha33_metadata_probe_endpoint_unchanged() -> None:
    data = _client().post(
        "/api/builder/workbook-metadata-probe-approval",
        json={"conversation_id": _cid("alpha34_alpha33_guard"), "client_event_id": "probe", "approval_granted": False},
    ).json()
    assert data["route"] == "builder_workbook_metadata_probe_approval"
    assert data["blocked"] is True
    assert data["reason"] == "engine_contract_not_found"
    assert data["workbook_opened"] is False
    assert data["sheet_names_read"] is False
    assert data["workbook_read"] is False


def test_alpha34_endpoint_owner_and_workbook_access_are_isolated() -> None:
    root = Path(__file__).resolve().parents[3]
    py_files = [p for p in (root / "jarvis_v5").rglob("*.py") if "__pycache__" not in p.parts]
    endpoint_refs = []
    logic_refs = []
    import_refs = []
    forbidden_source_refs = []
    import_token = "open" + "pyxl"
    forbidden_tokens = ["ws" + ".rows", "iter" + "_rows", "cell" + ".value", "calculate" + "_dimension", ".save(", "copyfile"]
    for path in py_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root).as_posix()
        if "workbook-sheet-name-probe-approval" in text:
            endpoint_refs.append(rel)
        if "evaluate_workbook_sheet_name_probe_approval" in text:
            logic_refs.append(rel)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == import_token:
                            import_refs.append(rel)
                elif isinstance(node, ast.ImportFrom):
                    if node.module == import_token:
                        import_refs.append(rel)
        if rel == "jarvis_v5/tools/builder/workbook_sheet_name_probe_approval.py":
            lowered = text.lower()
            for token in forbidden_tokens:
                if token in lowered:
                    forbidden_source_refs.append(token)
    assert "jarvis_v5/app.py" in endpoint_refs
    assert "jarvis_v5/tools/builder/workbook_sheet_name_probe_approval.py" in logic_refs
    runtime_logic_refs = [ref for ref in logic_refs if not ref.startswith("jarvis_v5/tests/")]
    assert runtime_logic_refs == [
        "jarvis_v5/app.py",
        "jarvis_v5/tools/builder/workbook_sheet_name_probe_approval.py",
    ]
    assert sorted(set(import_refs)) == [
        "jarvis_v5/tools/builder/workbook_sheet_name_probe_approval.py",
    ]
    assert forbidden_source_refs == []
