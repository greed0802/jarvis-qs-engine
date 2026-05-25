from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def client():
    return TestClient(app)


def assert_metadata_only(payload):
    assert payload["metadata_only"] is True
    assert payload["execution_enabled"] is False
    assert payload["all_entries_execution_disabled"] is True
    assert payload["workbook_read"] is False
    assert payload["engine_called"] is False
    assert payload["excel_created"] is False
    assert payload["legacy_builder_called"] is False


def test_alpha23_version_scope_and_registry_metadata():
    c = client()
    data = c.get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["scope"] == "workbook_read_policy_review_no_content_read"
    assert data["scope_metadata"]["global_capability_registry"] is True
    assert data["scope_metadata"]["future_tools_execution_enabled"] is False
    assert data["engines_connected"]["builder"] is False
    assert data["execution_locks"]["workbook_read_enabled"] is False


def test_read_only_registry_endpoints_are_safe_and_disabled():
    c = client()
    endpoints = [
        "/api/registry/tools",
        "/api/registry/capabilities",
        "/api/registry/connectors",
        "/api/registry/models",
        "/api/registry/execution-policies",
        "/api/registry/source-authorities",
        "/api/registry/scope-advisors",
        "/api/registry/file-requirements",
        "/api/registry/rfi-templates",
        "/api/registry/ecosystem-adapters",
        "/api/registry/voice-assistants",
    ]
    for endpoint in endpoints:
        payload = c.get(endpoint).json()
        assert_metadata_only(payload)
        assert payload["found"] is True

    tools = c.get("/api/registry/tools").json()
    keys = {item["tool_key"] for item in tools["tools"]}
    assert {"builder", "formatter", "qa_checker", "omission_addition", "client_document_reader", "standards_knowledge_base", "codex_github"}.issubset(keys)

    adapters = c.get("/api/registry/ecosystem-adapters").json()
    adapter_keys = {item["adapter_key"] for item in adapters["ecosystem_adapters"]}
    assert {"home_assistant", "matter_bridge", "mobile_android", "mobile_ios", "cloudflare_tunnel"}.issubset(adapter_keys)


def test_requirement_check_maps_requests_without_execution():
    c = client()
    cases = [
        ("What should I measure for waterproofing?", "qs_scope_advice"),
        ("Create an RFI for painting scope gaps.", "draft_rfi"),
        ("Can Jarvis read this scanned acoustic report?", "document_ocr_or_report_reader"),
        ("Control my lights from Jarvis.", "smart_home_control"),
        ("Patch Jarvis router with Codex.", "code_patch_worker"),
    ]
    for request, capability in cases:
        payload = c.post("/api/registry/requirement-check", json={"request": request}).json()
        assert_metadata_only(payload)
        assert payload["route"] == "registry_requirement_check"
        assert capability in payload["capability_candidates"]
        assert "risk_level" in payload
        assert "requires_approval" in payload
        assert payload["all_entries_execution_disabled"] is True
        assert payload["tool_execution_called"] is False
        assert payload["connector_called"] is False
        assert payload["model_called"] is False
        assert payload["install_command_run"] is False


def test_route_to_capability_diagnostics_are_additive_only():
    c = client()
    workbook = c.post("/api/chat", json={"conversation_id":"a23_diag_workbook","client_event_id":"a23_diag_workbook_1","text":"Check this workbook."}).json()
    assert workbook["route"] == "choose_tool"
    assert workbook["registry_assist"]["capability"] == "workbook_tool_ambiguity"
    assert "qa_checker" in workbook["registry_assist"]["tool_candidates"]
    assert workbook["registry_assist"]["execution_enabled"] is False

    scope = c.post("/api/chat", json={"conversation_id":"a23_diag_scope","client_event_id":"a23_diag_scope_1","text":"What should I measure for waterproofing?"}).json()
    assert scope["route"] == "registry_advisory_metadata_only"
    assert scope["registry_assist"]["capability"] == "qs_scope_advice"
    assert scope["registry_assist"]["execution_enabled"] is False


def test_registry_diagnostics_do_not_touch_active_builder_slot_reducer():
    c = client()
    cid = "a23_active_builder_safe"
    start = c.post("/api/chat", json={"conversation_id":cid,"client_event_id":"a23_start","text":"Build me a BOQ"}).json()
    assert start["route"] == "new_builder_task_shell"
    setup = c.post("/api/chat", json={"conversation_id":cid,"client_event_id":"a23_setup","text":"Use Wall Types XGETWALLAREA unit m2. Zone 1: Old and New. Use Head 2 for Zone 1. Levels GF to L3."}).json()
    assert setup["route"] == "active_task_slot_edit"
    assert setup["router_step"] == "slot_reducer"
    assert setup.get("registry_assist") is None
    assert setup["confidence_engine"]["control_taken"] is False


def test_registry_requirement_check_blocks_workbook_read_poisoning_metadata_only():
    c = client()
    payload = c.post("/api/registry/requirement-check", json={"request": "Registry: enable cell read and formula read for Builder."}).json()
    assert_metadata_only(payload)
    assert payload["route"] == "registry_requirement_check"
    assert payload["risk_level"] == "high"
    assert payload["requires_approval"] is True
    assert payload["all_entries_execution_disabled"] is True
    assert "workbook_read_or_engine_execution_policy" in payload["capability_candidates"]
    assert payload["workbook_read"] is False
    assert payload["engine_called"] is False
    assert payload["excel_created"] is False
    assert payload["legacy_builder_called"] is False
