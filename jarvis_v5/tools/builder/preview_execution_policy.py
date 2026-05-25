from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from jarvis_v5.config import (
    BUILDER_ENGINE_EXECUTION_ENABLED,
    LEGACY_BUILDER_CALLABLE,
    WORKBOOK_READ_ENABLED,
    EXCEL_OUTPUT_ENABLED,
)

NO_ENGINE_SAFETY = {
    "workbook_read": False,
    "engine_called": False,
    "excel_created": False,
    "contract_only": True,
    "legacy_builder_called": False,
}

PREVIEW_POLICY_VERSION = "preview_execution_policy_v1"
PREVIEW_RESULT_SCHEMA_VERSION = "builder_preview_result_v1"
OUTPUT_MANIFEST_SCHEMA_VERSION = "builder_output_manifest_v1"
BACKGROUND_JOB_POLICY_VERSION = "builder_background_job_policy_v1"
FAILURE_RECOVERY_POLICY_VERSION = "legacy_builder_failure_recovery_v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_policy_id() -> str:
    return f"preview_policy_{uuid.uuid4().hex}"


def _contract_payload(contract: Any | None) -> dict[str, Any] | None:
    if contract is None:
        return None
    if hasattr(contract, "model_dump"):
        return contract.model_dump(mode="json")
    if isinstance(contract, dict):
        return contract
    return None


def _contract_ready(payload: dict[str, Any] | None) -> bool:
    if not payload:
        return False
    if payload.get("contract_status") != "ready_for_engine_connection":
        return False
    validation = payload.get("validation") or {}
    if isinstance(validation, dict) and validation.get("valid") is False:
        return False
    setup = payload.get("builder_setup") or {}
    return bool(setup and payload.get("workbook_ref"))


RAW_PATH_LIKE_KEYS = {
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
    "saved_path",
    "path",
}


def _count_or_zero(value: Any) -> int:
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, (list, tuple, set)):
        return len(value)
    return 0


def _public_workbook_ref(workbook_ref: Any | None) -> dict[str, Any]:
    if not isinstance(workbook_ref, dict):
        return {"filename": None, "workbook_id": None, "source": None}
    return {
        "filename": workbook_ref.get("filename"),
        "workbook_id": workbook_ref.get("workbook_id"),
        "source": workbook_ref.get("source") or workbook_ref.get("kind") or "upload",
    }


def _public_contract_summary(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {
            "found": False,
            "ready": False,
            "contract_id": None,
            "contract_status": None,
            "schema_version": None,
            "validation_valid": False,
            "workbook_ref": _public_workbook_ref(None),
            "setup_summary": {
                "trade_profile": None,
                "costx_function": None,
                "custom_quantity": None,
                "unit": None,
                "zone_mode": None,
                "zone_count": 0,
                "heading_assignment_count": 0,
                "level_count": 0,
                "alias_count": 0,
                "item_code_enabled": False,
            },
        }
    setup = payload.get("builder_setup") or {}
    validation = payload.get("validation") or {}
    item_code_settings = setup.get("item_code_settings") or {}
    dynamic_zones = setup.get("dynamic_zones") or []
    heading_assignments = setup.get("heading_assignments") or {}
    levels = setup.get("levels") or []
    aliases = setup.get("aliases") or {}
    return {
        "found": True,
        "ready": _contract_ready(payload),
        "contract_id": payload.get("contract_id"),
        "contract_status": payload.get("contract_status"),
        "schema_version": payload.get("contract_schema_version"),
        "validation_valid": bool(validation.get("valid", False)),
        "workbook_ref": _public_workbook_ref(payload.get("workbook_ref")),
        "setup_summary": {
            "trade_profile": setup.get("trade_profile"),
            "costx_function": setup.get("costx_function"),
            "custom_quantity": setup.get("custom_quantity"),
            "unit": setup.get("unit"),
            "zone_mode": setup.get("zone_mode"),
            "zone_count": _count_or_zero(dynamic_zones),
            "heading_assignment_count": _count_or_zero(heading_assignments),
            "level_count": _count_or_zero(levels),
            "alias_count": _count_or_zero(aliases),
            "item_code_enabled": bool(item_code_settings.get("enabled", False)),
        },
    }


def _approval_token_policy() -> dict[str, Any]:
    return {
        "policy": "builder_approval_token_policy_v1",
        "status": "schema_defined_not_issued",
        "token_issued": False,
        "token_required_for_future_preview": True,
        "token_required_for_future_export": True,
        "execution_enabled": False,
        "required_future_fields": [
            "approval_token",
            "conversation_id",
            "contract_id",
            "requested_action",
            "issued_at",
            "expires_at",
            "approved_by_user_event_id",
            "contract_hash",
        ],
    }


def _preview_approval_readiness(*, contract_ready: bool, blocked_by_policy: list[str]) -> dict[str, Any]:
    return {
        "can_request_preview": False,
        "can_execute_preview": False,
        "approval_required": True,
        "approval_token_issued": False,
        "contract_ready": bool(contract_ready),
        "blocked_by_policy": list(blocked_by_policy),
    }


def _export_approval_readiness(*, contract_ready: bool, blocked_by_policy: list[str]) -> dict[str, Any]:
    blocked = list(blocked_by_policy)
    if "preview_approval_required_before_export" not in blocked:
        blocked.append("preview_approval_required_before_export")
    return {
        "can_request_export": False,
        "can_execute_export": False,
        "requires_successful_preview": True,
        "approval_required": True,
        "approval_token_issued": False,
        "contract_ready": bool(contract_ready),
        "blocked_by_policy": blocked,
    }


def _blocked_reason_details(blocked_by_policy: list[str]) -> list[dict[str, Any]]:
    messages = {
        "workbook_read_disabled": "Workbook reading is disabled by configuration.",
        "legacy_builder_callable_disabled": "Legacy Builder calling is disabled by configuration.",
        "excel_output_disabled": "Excel output creation is disabled by configuration.",
        "execution_kill_switch": "Builder execution kill switch is active.",
        "engine_contract_not_ready": "A ready Builder engine contract is required before preview execution.",
        "preview_approval_required_before_export": "Export requires a successful preview and explicit export approval first.",
    }
    return [
        {
            "code": code,
            "message": messages.get(code, "Blocked by preview/export execution policy."),
            "execution_enabled": False,
        }
        for code in blocked_by_policy
    ]


def _contains_raw_path_key(payload: Any) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in RAW_PATH_LIKE_KEYS:
                return True
            if _contains_raw_path_key(value):
                return True
    if isinstance(payload, list):
        return any(_contains_raw_path_key(item) for item in payload)
    return False


def _blocked_by_policy(*, contract_ready: bool, requested_action: str) -> list[str]:
    blocked: list[str] = []
    if not WORKBOOK_READ_ENABLED:
        blocked.append("workbook_read_disabled")
    if not LEGACY_BUILDER_CALLABLE:
        blocked.append("legacy_builder_callable_disabled")
    if not EXCEL_OUTPUT_ENABLED:
        blocked.append("excel_output_disabled")
    if not BUILDER_ENGINE_EXECUTION_ENABLED:
        blocked.append("execution_kill_switch")
    if not contract_ready:
        blocked.append("engine_contract_not_ready")
    if requested_action == "export":
        blocked.append("preview_approval_required_before_export")
    return blocked


def workbook_read_permission_boundary() -> dict[str, Any]:
    return {
        "policy": "workbook_read_permission_boundary_v1",
        "status": "defined_not_enabled",
        "enabled": False,
        "workbook_read_enabled": False,
        "required_before_future_read": [
            "active_builder_task",
            "attached_workbook_metadata",
            "current_snapshot",
            "current_adapter_dry_run",
            "ready_engine_contract",
            "boundary_audit_clean",
            "preflight_ready",
            "explicit_preview_approval",
            "workbook_read_enabled_config_true",
        ],
        "blocked_operations_now": [
            "open_workbook_file",
            "parse_workbook_sheets",
            "resolve_absolute_workbook_path_for_execution",
            "read_cell_values_or_formulas",
        ],
    }


def safe_workbook_path_resolver_policy() -> dict[str, Any]:
    return {
        "policy": "safe_workbook_path_resolver_v1",
        "status": "metadata_only",
        "allowed_now": [
            "read workbook_ref metadata already stored in contract",
            "display filename/workbook_id/source fields",
        ],
        "blocked_now": [
            "path traversal resolution",
            "filesystem existence probe for workbook file",
            "opening workbook file",
            "following external links or network paths",
        ],
        "future_requirements": [
            "attachment_id must resolve inside Jarvis attachment store",
            "resolved path must stay under approved data/attachments root",
            "file extension and content type must pass whitelist",
            "read approval must be tied to a current contract/preflight",
        ],
    }


def preview_approval_policy() -> dict[str, Any]:
    return {
        "policy": "preview_only_approval_policy_v1",
        "status": "defined_not_enabled",
        "preview_execution_enabled": False,
        "requires": [
            "ready_contract",
            "clean_boundary_audit",
            "preflight_ready",
            "explicit_user_approval_for_preview",
            "workbook_read_enabled",
            "legacy_builder_callable_enabled",
        ],
        "preview_outputs_allowed_later": [
            "preview_result_json",
            "preview_row_summary",
            "preview_safety_report",
        ],
        "outputs_blocked_now": [
            "preview_rows",
            "excel_workbook",
            "formula_generation",
            "legacy_builder_call",
        ],
    }


def export_approval_policy() -> dict[str, Any]:
    return {
        "policy": "export_approval_policy_v1",
        "status": "defined_not_enabled",
        "export_execution_enabled": False,
        "requires": [
            "preview_completed_successfully",
            "formula_integrity_guard_passed",
            "explicit_user_approval_for_export",
            "excel_output_enabled",
        ],
        "blocked_now": [
            "excel_file_creation",
            "download_manifest_creation_from_engine",
            "formatter_handoff_execution",
        ],
    }


def preview_result_schema() -> dict[str, Any]:
    return {
        "schema_version": PREVIEW_RESULT_SCHEMA_VERSION,
        "status": "defined_not_emitted_by_engine",
        "required_fields": [
            "preview_id",
            "conversation_id",
            "contract_id",
            "source_workbook_ref",
            "preview_status",
            "row_count",
            "zone_summary",
            "level_summary",
            "formula_integrity_status",
            "safety",
        ],
        "safety_defaults": dict(NO_ENGINE_SAFETY),
    }


def output_manifest_schema() -> dict[str, Any]:
    return {
        "schema_version": OUTPUT_MANIFEST_SCHEMA_VERSION,
        "status": "defined_not_created",
        "required_fields": [
            "manifest_id",
            "conversation_id",
            "source_contract_id",
            "output_type",
            "status",
            "files",
            "created_at",
            "safety",
        ],
        "allowed_future_output_types": ["builder_preview", "builder_export", "formatter_output", "qa_report"],
        "files_schema": {
            "file_id": "string",
            "filename": "string",
            "relative_path": "string_under_output_root",
            "content_type": "string",
            "size_bytes": "integer",
            "download_allowed": "boolean",
        },
    }


def background_job_boundary_plan() -> dict[str, Any]:
    return {
        "policy": BACKGROUND_JOB_POLICY_VERSION,
        "status": "planned_disabled",
        "job_enqueue_enabled": False,
        "future_required_fields": [
            "job_id",
            "conversation_id",
            "contract_id",
            "job_type",
            "approval_token",
            "created_at",
            "status",
            "safety",
        ],
        "blocked_now": ["enqueue_preview_job", "enqueue_export_job", "background_workbook_read"],
        "failure_rules": [
            "job failure must not mutate active Builder plan",
            "partial outputs are quarantined until validated",
            "failed preview/export must produce support-log evidence",
        ],
    }


def formula_integrity_guard_connection_point() -> dict[str, Any]:
    return {
        "policy": "formula_integrity_guard_connection_point_v1",
        "status": "planned_not_connected",
        "future_position": "after preview row/formula generation and before export approval",
        "must_validate": [
            "CostX function names",
            "units",
            "zone tokens",
            "level tokens",
            "custom quantities",
            "live Excel formula preservation",
            "duplicate token rows",
            "blocked preview/export on mismatch",
        ],
        "blocked_now": ["formula_generation", "formula_integrity_guard_execution"],
    }


def legacy_failure_recovery_contract() -> dict[str, Any]:
    return {
        "policy": FAILURE_RECOVERY_POLICY_VERSION,
        "status": "defined_for_future_use",
        "future_failure_routes": [
            "builder_preview_execution_failed",
            "builder_export_execution_failed",
        ],
        "recovery_rules": [
            "preserve active plan and contract",
            "do not mark preview/export ready",
            "quarantine partial output files",
            "surface safe user message and detailed debug evidence",
            "require rerun after correction",
        ],
        "blocked_now": ["legacy_builder_call", "partial_output_creation"],
    }


def evaluate_preview_execution_policy(
    *,
    conversation_id: str,
    client_event_id: str | None = None,
    contract: Any | None = None,
    requested_action: str = "preview",
) -> dict[str, Any]:
    """Return the metadata-only workbook/preview execution policy state.

    This owner is intentionally non-executing. It does not open files, resolve
    filesystem workbook paths, import/call the legacy Builder, enqueue jobs,
    generate formulas, or create output manifests. It only reports the policy
    gates required before those operations can be considered in a later alpha.
    """
    contract_payload = _contract_payload(contract)
    contract_found = contract_payload is not None
    contract_ready = _contract_ready(contract_payload)
    requested_action = requested_action if requested_action in {"preview", "export"} else "preview"
    blocked_by_policy = _blocked_by_policy(contract_ready=contract_ready, requested_action=requested_action)
    reason = "preview_execution_policy_blocked"
    if not contract_found:
        reason = "engine_contract_not_found"
    elif not contract_ready:
        reason = "engine_contract_not_ready"
    elif requested_action == "export":
        reason = "export_requires_completed_preview_and_approval"
    elif blocked_by_policy:
        reason = "preview_execution_disabled_by_policy"

    contract_summary = _public_contract_summary(contract_payload)
    return {
        "conversation_id": conversation_id,
        "client_event_id": client_event_id,
        "policy_id": new_policy_id(),
        "route": "builder_preview_execution_policy",
        "metadata_only": True,
        "execution_enabled": False,
        "blocked": True,
        "reason": reason,
        "message": "Preview/export execution policy evaluated. This is metadata-only: no workbook was read, no Builder engine was called, no job was enqueued, and no Excel output was created.",
        **NO_ENGINE_SAFETY,
        "safety": {
            **dict(NO_ENGINE_SAFETY),
            "contract_summary_public_only": True,
            "raw_contract_payload_returned": False,
            "contract_summary_has_raw_path_key": _contains_raw_path_key(contract_summary),
        },
        "requested_action": requested_action,
        "contract_found": contract_found,
        "contract_id": contract_payload.get("contract_id") if contract_payload else None,
        "contract_ready": contract_ready,
        "policy_version": PREVIEW_POLICY_VERSION,
        "blocked_by_policy": blocked_by_policy,
        "execution_locks": {
            "builder_engine_execution_enabled": bool(BUILDER_ENGINE_EXECUTION_ENABLED),
            "legacy_builder_callable": bool(LEGACY_BUILDER_CALLABLE),
            "workbook_read_enabled": bool(WORKBOOK_READ_ENABLED),
            "excel_output_enabled": bool(EXCEL_OUTPUT_ENABLED),
        },
        "workbook_read_permission_boundary": workbook_read_permission_boundary(),
        "safe_workbook_path_resolver": safe_workbook_path_resolver_policy(),
        "preview_approval_policy": preview_approval_policy(),
        "export_approval_policy": export_approval_policy(),
        "preview_result_schema": preview_result_schema(),
        "output_manifest_schema": output_manifest_schema(),
        "background_job_boundary": background_job_boundary_plan(),
        "formula_integrity_guard_connection_point": formula_integrity_guard_connection_point(),
        "failure_recovery_contract": legacy_failure_recovery_contract(),
        "contract": None,
        "contract_summary": contract_summary,
        "approval_token_policy": _approval_token_policy(),
        "preview_approval_readiness": _preview_approval_readiness(contract_ready=contract_ready, blocked_by_policy=blocked_by_policy),
        "export_approval_readiness": _export_approval_readiness(contract_ready=contract_ready, blocked_by_policy=blocked_by_policy),
        "blocked_reason_details": _blocked_reason_details(blocked_by_policy),
        "next_safe_action": "Keep workbook read and execution disabled. Review policy gates before any future preview execution alpha.",
        "created_at": now_iso(),
    }
