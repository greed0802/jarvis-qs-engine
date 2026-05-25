from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.integrity_contract_schema import (
    ApprovalEscalationSpec,
    AuditEventRequirementSpec,
    BlockedTransitionSpec,
    ExecutionTierSpec,
    FutureToolRollbackPolicySpec,
    IntegrityContractMapResponse,
    IntegritySafetyEnvelope,
    ReadinessGateSpec,
    StateTransitionSpec,
    ToolRiskTierSpec,
)

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "jarvis_v5" / "registry"
DOCS = ROOT / "jarvis_v5" / "docs"


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


def test_alpha36_0_version_and_locks() -> None:
    data = _client().get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False


def test_integrity_schema_defaults_are_no_execution_no_read() -> None:
    safety = IntegritySafetyEnvelope()
    assert safety.metadata_only is True
    assert safety.execution_enabled is False
    assert safety.workbook_read is False
    assert safety.workbook_content_read is False
    assert safety.sheet_name_probe_allowed is False
    assert safety.formula_read is False
    assert safety.cell_value_read is False
    assert safety.engine_called is False
    assert safety.excel_created is False

    tier = ExecutionTierSpec(tier_key="metadata_probe_future", tier=2, display_name="Metadata probe", allowed_in_alpha36_0=False)
    assert tier.execution_enabled is False
    assert tier.safety.sheet_name_probe_allowed is False

    transition = StateTransitionSpec(from_state="metadata_only", to_state="sheet_name_probe", blocked_reason="sheet_name_probe_not_approved")
    assert transition.allowed is False
    assert transition.safety.workbook_read is False

    blocked = BlockedTransitionSpec(transition_key="metadata_to_cell_read", from_state="metadata_only", to_state="cell_value_read", blocked_reason="cell_value_read_not_approved")
    assert blocked.execution_enabled is False
    assert blocked.safety.cell_value_read is False

    approval = ApprovalEscalationSpec(approval_level="sheet_name_probe_approval_future", risk_tier_required=2)
    assert approval.grants_runtime_permission is False
    assert approval.safety.sheet_name_probe_allowed is False

    audit = AuditEventRequirementSpec(event_type="read_blocked", required_fields=["event_id", "safety_snapshot"])
    assert audit.writes_runtime_event is False
    assert audit.safety_snapshot.workbook_read is False

    rollback = FutureToolRollbackPolicySpec(tool_key="builder", rollback_policy_key="builder_export_requires_rollback_package", output_only=False)
    assert rollback.execution_enabled is False
    assert rollback.destructive_delete_allowed is False

    gate = ReadinessGateSpec(gate_key="explicit_user_sheet_name_probe_approval", description="Future approval only")
    assert gate.satisfied_in_alpha36_0 is False
    assert gate.safety.sheet_name_probe_allowed is False

    response = IntegrityContractMapResponse(version=APP_VERSION, execution_tiers=[tier], blocked_transitions=[blocked], readiness_gates=[gate])
    assert response.workbook_read is False
    assert response.workbook_content_read is False
    assert response.sheet_name_probe_allowed is False
    assert response.formula_read is False
    assert response.cell_value_read is False


def test_registry_integrity_metadata_keeps_all_read_flags_false() -> None:
    bad_true_keys = {
        "execution_enabled",
        "workbook_read",
        "workbook_content_read",
        "sheet_name_probe_allowed",
        "formula_read",
        "cell_value_read",
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


def test_tool_risk_tiers_keep_builder_export_highest_risk() -> None:
    tools = json.loads((REGISTRY / "tool_registry.json").read_text())["tools"]
    by_key = {t["tool_key"]: t for t in tools}
    assert by_key["builder"]["execution_risk_tier"] == 7
    assert by_key["builder"]["execution_enabled"] is False
    assert by_key["builder"]["engine_called"] is False
    assert by_key["formatter"]["execution_risk_tier"] >= 6
    assert by_key["qa_checker"]["execution_risk_tier"] >= 4


def test_execution_policies_include_integrity_contracts_disabled() -> None:
    policies = json.loads((REGISTRY / "execution_policy_registry.json").read_text())["policies"]
    by_key = {p["policy_key"]: p for p in policies}
    for key in ["pre_execution_integrity_matrix", "state_transition_contract", "sheet_name_probe_readiness_gates"]:
        assert by_key[key]["metadata_only"] is True
        assert by_key[key]["execution_enabled"] is False
        assert by_key[key]["workbook_read"] is False
        assert by_key[key]["sheet_name_probe_allowed"] is False


def test_direct_workbook_probe_request_still_safe_blocked() -> None:
    response = _client().post(
        "/api/chat",
        json={
            "conversation_id": "alpha360_direct_probe_block",
            "client_event_id": "alpha360_direct_probe_block",
            "text": "Probe this workbook and list sheet names, formulas, and cell values.",
        },
    ).json()
    assert response["workbook_read"] is False
    assert response["engine_called"] is False
    assert response["excel_created"] is False
    assert response["legacy_builder_called"] is False


def test_alpha36_0_docs_exist() -> None:
    for name in [
        "ALPHA_36_0_SCOPE.md",
        "PRE_EXECUTION_INTEGRITY_MATRIX.md",
        "STATE_TRANSITION_CONTRACT.md",
        "APPROVAL_ESCALATION_CONTRACT.md",
        "BLOCKED_TRANSITION_LIST.md",
        "AUDIT_EVENT_REQUIREMENT.md",
        "FUTURE_TOOL_ROLLBACK_POLICY.md",
        "SHEET_NAME_PROBE_READINESS_GATES.md",
        "ROADMAP_AFTER_ALPHA_35_19.md",
    ]:
        assert (DOCS / name).exists(), name
