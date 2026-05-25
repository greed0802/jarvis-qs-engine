from __future__ import annotations

from typing import Any

NO_ENGINE_SAFETY = {
    "workbook_read": False,
    "engine_called": False,
    "excel_created": False,
    "contract_only": True,
    "legacy_builder_called": False,
}

ALLOWED_METADATA_FIELDS = [
    "workbook_id",
    "attachment_id",
    "filename",
    "extension",
    "content_type",
    "size_bytes",
    "source",
    "conversation_id",
    "contract_id",
    "workbook_ref_found",
    "metadata_validation",
]

BLOCKED_OPERATIONS = [
    "open_workbook",
    "parse_workbook",
    "read_sheet_names",
    "read_cells",
    "read_formulas",
    "read_workbook_dimensions",
    "generate_formulas",
    "call_builder_engine",
    "call_legacy_builder",
    "create_excel",
    "upgrade_preview_readiness",
    "upgrade_export_readiness",
]

ALLOWED_EXTENSIONS = [".xlsx", ".xlsm"]
ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel.sheet.macroEnabled.12",
    "application/vnd.ms-excel",
    None,
}

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


def _contract_payload(contract: Any | None) -> dict[str, Any] | None:
    if contract is None:
        return None
    if hasattr(contract, "model_dump"):
        payload = contract.model_dump(mode="json")
        return payload if isinstance(payload, dict) else None
    return contract if isinstance(contract, dict) else None


def _extension_from_filename(filename: Any | None) -> str | None:
    if not isinstance(filename, str) or not filename.strip() or "." not in filename:
        return None
    return "." + filename.strip().lower().rsplit(".", 1)[-1]


def _public_workbook_metadata(workbook_ref: Any | None) -> dict[str, Any]:
    if not isinstance(workbook_ref, dict) or not workbook_ref:
        return {
            "filename": None,
            "extension": None,
            "workbook_id": None,
            "attachment_id": None,
            "source": None,
            "content_type": None,
            "size_bytes": None,
        }
    filename = workbook_ref.get("filename")
    return {
        "filename": filename,
        "extension": _extension_from_filename(filename),
        "workbook_id": workbook_ref.get("workbook_id"),
        "attachment_id": workbook_ref.get("attachment_id"),
        "source": workbook_ref.get("source") or workbook_ref.get("kind") or "upload",
        "content_type": workbook_ref.get("content_type"),
        "size_bytes": workbook_ref.get("size_bytes"),
    }


def _metadata_validation(metadata: dict[str, Any], workbook_ref_found: bool) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    extension = metadata.get("extension")
    content_type = metadata.get("content_type")
    size_bytes = metadata.get("size_bytes")
    if not workbook_ref_found:
        issues.append("workbook_ref_not_found")
    if not metadata.get("filename"):
        issues.append("filename_missing")
    if extension not in ALLOWED_EXTENSIONS:
        issues.append("extension_not_allowed")
    if content_type not in ALLOWED_CONTENT_TYPES:
        warnings.append("content_type_not_recognized_for_excel")
    if size_bytes is None:
        warnings.append("size_bytes_missing")
        size_valid = False
    else:
        size_valid = isinstance(size_bytes, int) and size_bytes > 0
        if not size_valid:
            issues.append("size_bytes_invalid")
    valid = bool(workbook_ref_found and metadata.get("filename") and extension in ALLOWED_EXTENSIONS)
    # Missing size/content-type are allowed warnings for older attachment metadata.
    return {
        "valid": valid,
        "metadata_probe_candidate_allowed": valid,
        "extension_allowed": extension in ALLOWED_EXTENSIONS,
        "content_type_allowed": content_type in ALLOWED_CONTENT_TYPES,
        "size_valid": size_valid,
        "issues": issues,
        "warnings": warnings,
    }


def _contains_forbidden_exact_key(payload: Any) -> bool:
    if isinstance(payload, dict):
        return any(str(k) in FORBIDDEN_EXACT_RAW_PATH_KEYS or _contains_forbidden_exact_key(v) for k, v in payload.items())
    if isinstance(payload, list):
        return any(_contains_forbidden_exact_key(v) for v in payload)
    return False


def _collect_raw_path_values(payload: Any) -> set[str]:
    values: set[str] = set()
    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                if str(key) in FORBIDDEN_EXACT_RAW_PATH_KEYS and isinstance(nested, str) and nested:
                    values.add(nested)
                walk(nested)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(payload)
    return values


def _payload_contains_value(payload: Any, raw_values: set[str]) -> bool:
    if not raw_values:
        return False
    if isinstance(payload, str):
        return payload in raw_values
    if isinstance(payload, dict):
        return any(_payload_contains_value(v, raw_values) for v in payload.values())
    if isinstance(payload, list):
        return any(_payload_contains_value(v, raw_values) for v in payload)
    return False


def evaluate_workbook_metadata_probe_approval(
    *,
    conversation_id: str,
    client_event_id: str | None = None,
    contract: Any | None = None,
    approval_granted: bool = False,
) -> dict[str, Any]:
    """Evaluate a user-facing workbook metadata probe approval contract.

    This function reads only already-stored Jarvis contract/workbook_ref metadata.
    It never opens, parses, reads, resolves, stats, copies, or inspects workbook
    files and it never mutates Builder state or readiness.
    """
    contract_payload = _contract_payload(contract)
    contract_found = contract_payload is not None
    workbook_ref = contract_payload.get("workbook_ref") if contract_payload else None
    workbook_ref_found = isinstance(workbook_ref, dict) and bool(workbook_ref)
    metadata = _public_workbook_metadata(workbook_ref)
    validation = _metadata_validation(metadata, workbook_ref_found)
    raw_values = _collect_raw_path_values(workbook_ref or {})

    approval_required = not bool(approval_granted)
    blocked_by_policy = [
        "metadata_only_contract",
        "workbook_open_disabled",
        "workbook_read_disabled",
        "workbook_parse_disabled",
        "sheet_names_read_disabled",
        "execution_kill_switch",
    ]
    if not contract_found:
        reason = "engine_contract_not_found"
        blocked = True
        blocked_by_policy.append("engine_contract_not_found")
    elif not workbook_ref_found:
        reason = "workbook_ref_not_found"
        blocked = True
        blocked_by_policy.append("workbook_ref_not_found")
    elif approval_required:
        reason = "metadata_probe_approval_required"
        blocked = True
        blocked_by_policy.append("metadata_probe_approval_required")
    elif not validation.get("valid"):
        reason = "workbook_metadata_not_safe_for_probe"
        blocked = True
        blocked_by_policy.append("metadata_validation_failed")
    else:
        reason = "metadata_probe_approved_metadata_only"
        blocked = False

    safety = {
        **dict(NO_ENGINE_SAFETY),
        "metadata_only": True,
        "execution_enabled": False,
        "workbook_opened": False,
        "workbook_read": False,
        "workbook_parsed": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "raw_path_value_returned": False,
        "forbidden_path_key_returned": False,
        "preview_readiness_upgraded": False,
        "export_readiness_upgraded": False,
    }

    response = {
        "conversation_id": conversation_id,
        "client_event_id": client_event_id,
        "contract_id": contract_payload.get("contract_id") if contract_payload else None,
        "route": "builder_workbook_metadata_probe_approval",
        "message": "Workbook metadata probe approval evaluated metadata only. No workbook was opened, parsed, or read.",
        "metadata_only": True,
        "execution_enabled": False,
        "approval_required": approval_required,
        "approval_granted": bool(approval_granted),
        "blocked": blocked,
        "reason": reason,
        "contract_found": contract_found,
        "workbook_ref_found": workbook_ref_found,
        "allowed_metadata_fields": list(ALLOWED_METADATA_FIELDS),
        "blocked_operations": list(BLOCKED_OPERATIONS),
        "blocked_by_policy": blocked_by_policy,
        "workbook_metadata": metadata,
        "metadata_validation": validation,
        "workbook_opened": False,
        "workbook_read": False,
        "workbook_parsed": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
        "raw_path_value_returned": False,
        "forbidden_path_key_returned": False,
        "preview_readiness_upgraded": False,
        "export_readiness_upgraded": False,
        "safety": safety,
        "readiness": {
            "status": "metadata_probe_blocked" if blocked else "metadata_probe_approved_metadata_only",
            "metadata_probe_candidate_allowed": bool(validation.get("metadata_probe_candidate_allowed")),
            "preview_readiness_upgraded": False,
            "export_readiness_upgraded": False,
            "next_gate": "future_sheet_name_probe_approval" if not blocked else "grant_metadata_probe_approval_or_fix_contract",
            "blocked_by_policy": blocked_by_policy,
        },
        "next_safe_action": "Review the metadata-only summary. Sheet names and workbook content remain blocked until a later explicit approval gate.",
    }
    response["forbidden_path_key_returned"] = _contains_forbidden_exact_key(response)
    response["raw_path_value_returned"] = _payload_contains_value(response, raw_values)
    response["safety"]["forbidden_path_key_returned"] = response["forbidden_path_key_returned"]
    response["safety"]["raw_path_value_returned"] = response["raw_path_value_returned"]
    return response
