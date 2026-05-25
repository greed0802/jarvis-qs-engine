from __future__ import annotations

from io import BytesIO
from fastapi.testclient import TestClient
from uuid import uuid4

from jarvis_v5.app import app


def client() -> TestClient:
    return TestClient(app)


def post_chat(c: TestClient, conversation_id: str, event_id: str, text: str) -> dict:
    return c.post(
        "/api/chat",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "text": text},
    ).json()


def attach_workbook(c: TestClient, conversation_id: str, event_id: str, filename: str = "Steel_test.xlsx") -> dict:
    return c.post(
        "/api/attach",
        data={"conversation_id": conversation_id, "client_event_id": event_id, "text": "Here"},
        files={"file": (filename, BytesIO(b"fake workbook bytes - not read"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    ).json()


def create_snapshot(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post(
        "/api/builder/create-snapshot",
        json={"conversation_id": conversation_id, "client_event_id": event_id, "approve": True},
    ).json()


def adapter_dry_run(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post(
        "/api/builder/adapter-dry-run",
        json={"conversation_id": conversation_id, "client_event_id": event_id},
    ).json()


def setup_flow(c: TestClient, conv: str) -> None:
    post_chat(c, conv, f"{conv}_001", "Build me a BOQ")
    attach_workbook(c, conv, f"{conv}_attach")
    post_chat(c, conv, f"{conv}_zone", "Zone 1: Old and New")


def test_plan_reports_setup_completeness_with_missing_slots():
    c = client()
    conv = f"alpha7_plan_completeness_{uuid4().hex}"
    setup_flow(c, conv)

    plan = c.get(f"/api/plan/{conv}").json()
    setup = plan["setup_completeness"]
    assert plan["workbook"]["found"] is True
    assert setup["status"] == "incomplete"
    assert setup["ready_for_dry_run"] is True
    assert setup["ready_for_future_engine"] is False
    assert "trade_profile" in setup["missing_required"]
    assert "costx_function" in setup["missing_required"]
    assert "unit" in setup["missing_required"]
    assert "heading_assignments" in setup["missing_required"]
    assert "levels" in setup["missing_required"]


def test_snapshot_and_adapter_include_setup_completeness_without_engine_or_workbook_read():
    c = client()
    conv = f"alpha7_snapshot_adapter_completeness_{uuid4().hex}"
    setup_flow(c, conv)

    snap = create_snapshot(c, conv, "a7_snap_001")
    assert snap["snapshot_status"] == "current"
    assert snap["setup_completeness"]["ready_for_dry_run"] is True
    assert snap["setup_completeness"]["ready_for_future_engine"] is False
    assert "No workbook attached" not in snap["validation"]["warnings"]

    dry = adapter_dry_run(c, conv, "a7_adapter_001")
    assert dry["route"] == "builder_adapter_dry_run"
    assert dry["blocked"] is False
    assert dry["workbook_read"] is False
    assert dry["engine_called"] is False
    assert dry["excel_created"] is False
    assert dry["setup_completeness"]["status"] == "incomplete"
    assert dry["setup_completeness"]["ready_for_future_engine"] is False
    assert dry["adapter_input"]["setup_completeness"]["ready_for_future_engine"] is False


def test_review_and_preview_stub_show_setup_completeness():
    c = client()
    conv = f"alpha7_review_preview_completeness_{uuid4().hex}"
    setup_flow(c, conv)
    create_snapshot(c, conv, "a7rp_snap_001")

    review = post_chat(c, conv, "a7rp_review", "Review")
    assert review["route"] == "active_task_review"
    assert "Setup completeness" in review["message"]
    assert "Future engine: not ready" in review["message"]
    assert review["setup_completeness"]["ready_for_future_engine"] is False

    preview = post_chat(c, conv, "a7rp_preview", "Preview")
    assert preview["route"] == "active_task_preview_stub"
    assert preview["blocked"] is True
    assert preview["reason"] == "preview_engine_not_connected"
    assert "No Builder engine was called" in preview["message"]
    assert "Future engine readiness: not ready" in preview["message"]
    assert preview["setup_completeness"]["ready_for_future_engine"] is False


def test_stale_snapshot_keeps_future_engine_not_ready():
    c = client()
    conv = f"alpha7_stale_completeness_{uuid4().hex}"
    setup_flow(c, conv)
    create_snapshot(c, conv, "a7s_snap_001")
    adapter_dry_run(c, conv, "a7s_adapter_001")
    post_chat(c, conv, "a7s_change", "Add Same to Zone 1")

    plan = c.get(f"/api/plan/{conv}").json()
    assert plan["snapshot"]["status"] == "stale"
    assert plan["adapter_dry_run"]["freshness"] == "stale"
    assert plan["setup_completeness"]["ready_for_future_engine"] is False
    assert "snapshot_current" in plan["setup_completeness"]["missing_required"]
