from __future__ import annotations

from typing import Any

from jarvis_v5.tools.builder.safe_workbook_path_resolver import evaluate_safe_workbook_path_resolver_dry_run

NO_ENGINE_SAFETY = {
    "workbook_read": False,
    "engine_called": False,
    "excel_created": False,
    "contract_only": True,
    "legacy_builder_called": False,
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

ALLOWED_EXTENSIONS = [".xlsx", ".xlsm"]
REJECTED_EXTENSIONS = [".pdf", ".zip", ".csv"]
ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel.sheet.macroEnabled.12",
    "application/vnd.ms-excel",
}


def _workbook_preflight_contract_payload(contract: Any | None) -> dict[str, Any] | None:
    if contract is None:
        return None
    if hasattr(contract, "model_dump"):
        payload = contract.model_dump(mode="json")
        return payload if isinstance(payload, dict) else None
    if isinstance(contract, dict):
        return contract
    return None


def _workbook_preflight_public_workbook_summary(workbook_ref: Any | None) -> dict[str, Any]:
    if not isinstance(workbook_ref, dict) or not workbook_ref:
        return {
            "found": False,
            "filename": None,
            "workbook_id": None,
            "attachment_id": None,
            "source": None,
            "content_type": None,
            "size_bytes": None,
        }
    return {
        "found": True,
        "filename": workbook_ref.get("filename"),
        "workbook_id": workbook_ref.get("workbook_id"),
        "attachment_id": workbook_ref.get("attachment_id"),
        "source": workbook_ref.get("source") or workbook_ref.get("kind") or "upload",
        "content_type": workbook_ref.get("content_type"),
        "size_bytes": workbook_ref.get("size_bytes"),
    }


def _workbook_preflight_extension_from_filename(filename: Any | None) -> str | None:
    if not isinstance(filename, str) or not filename.strip():
        return None
    clean = filename.strip().lower()
    if "." not in clean:
        return None
    return "." + clean.rsplit(".", 1)[-1]


def _workbook_preflight_extension_policy(extension: str | None) -> dict[str, Any]:
    return {
        "extension": extension,
        "extension_allowed": extension in ALLOWED_EXTENSIONS,
        "allowed_extensions": list(ALLOWED_EXTENSIONS),
        "rejected_extensions": list(REJECTED_EXTENSIONS),
    }


def _workbook_preflight_metadata_validation(summary: dict[str, Any], extension_policy: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    filename = summary.get("filename")
    content_type = summary.get("content_type")
    size_bytes = summary.get("size_bytes")
    extension = extension_policy.get("extension")

    if not summary.get("found"):
        issues.append("workbook_ref_not_found")
    if not filename:
        issues.append("filename_missing")
    if extension is None:
        issues.append("extension_missing")
    elif not extension_policy.get("extension_allowed"):
        issues.append("extension_not_allowed")
    if size_bytes is None:
        warnings.append("size_bytes_missing")
        size_valid = False
    else:
        size_valid = isinstance(size_bytes, int) and size_bytes > 0
        if not size_valid:
            issues.append("size_bytes_invalid")
    content_type_allowed = content_type in ALLOWED_CONTENT_TYPES
    if not content_type:
        warnings.append("content_type_missing")
    elif not content_type_allowed:
        warnings.append("content_type_not_recognized_for_excel")

    extension_allowed = bool(extension_policy.get("extension_allowed"))
    metadata_valid = bool(summary.get("found")) and bool(filename) and extension_allowed and size_valid
    metadata_complete = metadata_valid
    return {
        "valid": metadata_valid,
        "workbook_metadata_valid": metadata_valid,
        "workbook_metadata_complete": metadata_complete,
        "workbook_candidate_metadata_complete": metadata_complete,
        "workbook_candidate_allowed_by_metadata": False,
        "workbook_read_allowed": False,
        "workbook_open_allowed": False,
        "filename_present": bool(filename),
        "extension_allowed": extension_allowed,
        "content_type_allowed": content_type_allowed,
        "size_valid": size_valid,
        "issues": issues,
        "warnings": warnings,
    }


def _workbook_preflight_collect_raw_path_values(payload: Any) -> set[str]:
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


def _workbook_preflight_contains_forbidden_exact_key(payload: Any) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_EXACT_RAW_PATH_KEYS:
                return True
            if _workbook_preflight_contains_forbidden_exact_key(value):
                return True
    elif isinstance(payload, list):
        return any(_workbook_preflight_contains_forbidden_exact_key(item) for item in payload)
    return False


def _workbook_preflight_payload_contains_value(payload: Any, raw_values: set[str]) -> bool:
    if not raw_values:
        return False
    if isinstance(payload, str):
        return payload in raw_values
    if isinstance(payload, dict):
        return any(_workbook_preflight_payload_contains_value(value, raw_values) for value in payload.values())
    if isinstance(payload, list):
        return any(_workbook_preflight_payload_contains_value(item, raw_values) for item in payload)
    return False


def _workbook_preflight_safety_summary(*, metadata_validation: dict[str, Any], path_resolver_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy": "workbook_read_preflight_contract_v1",
        "status": "metadata_only_preflight_blocked",
        "metadata_validation_valid": bool(metadata_validation.get("valid")),
        "path_resolver_contract_available": bool(path_resolver_summary.get("contract_found")),
        "workbook_opened": False,
        "workbook_read": False,
        "workbook_parsed": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "engine_called": False,
        "excel_created": False,
        "legacy_builder_called": False,
        "raw_path_value_returned": False,
        "forbidden_path_key_returned": False,
    }


def evaluate_workbook_read_preflight_dry_run(
    *,
    conversation_id: str,
    client_event_id: str | None = None,
    contract: Any | None = None,
) -> dict[str, Any]:
    """Evaluate future workbook-read eligibility from Jarvis metadata only.

    This is not workbook reading. It does not resolve, stat, open, parse, or
    inspect workbook files. It only evaluates already-stored Jarvis contract
    metadata and reports whether a future read preflight would have enough
    public metadata to continue to the next approval gate.
    """
    contract_payload = _workbook_preflight_contract_payload(contract)
    contract_found = contract_payload is not None
    workbook_ref = contract_payload.get("workbook_ref") if contract_payload else None
    workbook_ref_found = isinstance(workbook_ref, dict) and bool(workbook_ref)
    workbook_summary = _workbook_preflight_public_workbook_summary(workbook_ref)
    extension = _workbook_preflight_extension_from_filename(workbook_summary.get("filename"))
    extension_policy = _workbook_preflight_extension_policy(extension)
    metadata_validation = _workbook_preflight_metadata_validation(workbook_summary, extension_policy)
    path_resolver_summary = evaluate_safe_workbook_path_resolver_dry_run(
        conversation_id=conversation_id,
        client_event_id=client_event_id,
        contract=contract,
    )
    raw_values = _workbook_preflight_collect_raw_path_values(workbook_ref or {})

    blocked_by_policy = [
        "metadata_only_preflight",
        "workbook_open_disabled",
        "workbook_read_disabled",
        "workbook_parse_disabled",
        "execution_kill_switch",
    ]
    if not contract_found:
        reason = "engine_contract_not_found"
        blocked_by_policy.append("engine_contract_not_found")
    elif not workbook_ref_found:
        reason = "workbook_ref_not_found"
        blocked_by_policy.append("workbook_ref_not_found")
    elif not extension_policy.get("extension_allowed"):
        reason = "workbook_extension_not_allowed"
        blocked_by_policy.append("extension_not_allowed")
    else:
        reason = "workbook_read_preflight_contract_only"

    future_required_checks = [
        "explicit_workbook_read_approval_token_required",
        "attachment_id_must_resolve_inside_jarvis_attachment_store",
        "resolved_file_must_remain_under_approved_attachment_root",
        "workbook_file_integrity_check_must_run_before_any_parse",
        "read_scope_must_be_limited_to_metadata_before_sheet_or_cell_access",
    ]

    safety = {
        **dict(NO_ENGINE_SAFETY),
        "metadata_only": True,
        "preflight_only": True,
        "execution_enabled": False,
        "workbook_opened": False,
        "workbook_read": False,
        "workbook_parsed": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "raw_path_value_returned": False,
        "forbidden_path_key_returned": False,
    }
    response = {
        "conversation_id": conversation_id,
        "client_event_id": client_event_id,
        "contract_id": contract_payload.get("contract_id") if contract_payload else None,
        "route": "builder_workbook_read_preflight_dry_run",
        "message": "Workbook read preflight contract evaluated Jarvis metadata only. No workbook was resolved, opened, parsed, or read.",
        "metadata_only": True,
        "preflight_only": True,
        "execution_enabled": False,
        "blocked": True,
        "reason": reason,
        "contract_found": contract_found,
        "workbook_ref_found": workbook_ref_found,
        "path_resolver_contract_available": bool(path_resolver_summary.get("contract_found")),
        "workbook_metadata_valid": bool(metadata_validation.get("workbook_metadata_valid")),
        "workbook_metadata_complete": bool(metadata_validation.get("workbook_metadata_complete")),
        "workbook_candidate_metadata_complete": bool(metadata_validation.get("workbook_candidate_metadata_complete")),
        "workbook_candidate_allowed_by_metadata": False,
        "workbook_read_allowed": False,
        "workbook_open_allowed": False,
        "filename": workbook_summary.get("filename"),
        "workbook_id": workbook_summary.get("workbook_id"),
        "attachment_id": workbook_summary.get("attachment_id"),
        "source": workbook_summary.get("source"),
        "content_type": workbook_summary.get("content_type"),
        "content_type_allowed": bool(metadata_validation.get("content_type_allowed")),
        "size_bytes": workbook_summary.get("size_bytes"),
        "size_valid": bool(metadata_validation.get("size_valid")),
        **extension_policy,
        "blocked_by_policy": blocked_by_policy,
        "metadata_validation": metadata_validation,
        "future_required_checks": future_required_checks,
        "path_resolver_summary": {
            "route": path_resolver_summary.get("route"),
            "contract_found": path_resolver_summary.get("contract_found"),
            "workbook_ref_found": path_resolver_summary.get("workbook_ref_found"),
            "workbook_ref_summary": path_resolver_summary.get("workbook_ref_summary"),
            "raw_saved_path_present": path_resolver_summary.get("raw_saved_path_present"),
            "path_like_metadata_present": path_resolver_summary.get("path_like_metadata_present"),
            "path_resolved": False,
            "filesystem_checked": False,
            "workbook_filesystem_checked": False,
            "workbook_opened": False,
            "workbook_read": False,
            "raw_path_value_returned": False,
            "forbidden_path_key_returned": False,
        },
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
        "safety": safety,
        "preflight_safety_summary": _workbook_preflight_safety_summary(
            metadata_validation=metadata_validation,
            path_resolver_summary=path_resolver_summary,
        ),
        "readiness": {
            "status": "blocked_metadata_only_preflight",
            "candidate_metadata_complete": bool(metadata_validation.get("workbook_candidate_metadata_complete")),
            "candidate_allowed_by_metadata": False,
            "workbook_read_allowed": False,
            "workbook_open_allowed": False,
            "next_gate": "future_explicit_workbook_read_approval",
            "blocked_by_policy": blocked_by_policy,
        },
        "next_safe_action": "Keep workbook open/read disabled. Use this preflight contract to verify workbook metadata before any future read approval alpha.",
    }
    response["forbidden_path_key_returned"] = _workbook_preflight_contains_forbidden_exact_key(response)
    response["raw_path_value_returned"] = _workbook_preflight_payload_contains_value(response, raw_values)
    response["safety"]["forbidden_path_key_returned"] = response["forbidden_path_key_returned"]
    response["safety"]["raw_path_value_returned"] = response["raw_path_value_returned"]
    response["preflight_safety_summary"]["forbidden_path_key_returned"] = response["forbidden_path_key_returned"]
    response["preflight_safety_summary"]["raw_path_value_returned"] = response["raw_path_value_returned"]
    return response
