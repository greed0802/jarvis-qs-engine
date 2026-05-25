from __future__ import annotations

from typing import Any

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


def _resolver_contract_payload(contract: Any | None) -> dict[str, Any] | None:
    if contract is None:
        return None
    if hasattr(contract, "model_dump"):
        payload = contract.model_dump(mode="json")
        return payload if isinstance(payload, dict) else None
    if isinstance(contract, dict):
        return contract
    return None


def _resolver_public_workbook_ref_summary(workbook_ref: Any | None) -> dict[str, Any]:
    if not isinstance(workbook_ref, dict):
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


def _resolver_detect_path_metadata(payload: Any) -> dict[str, Any]:
    found_keys: set[str] = set()
    saved_path_present = False

    def walk(value: Any) -> None:
        nonlocal saved_path_present
        if isinstance(value, dict):
            for key, nested in value.items():
                key_text = str(key)
                if key_text in FORBIDDEN_EXACT_RAW_PATH_KEYS:
                    found_keys.add(key_text)
                    if key_text == "saved_path":
                        saved_path_present = True
                walk(nested)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)
    return {
        "raw_saved_path_present": saved_path_present,
        "path_like_metadata_present": bool(found_keys),
        "path_like_keys_present_internal_only": sorted(found_keys),
    }


def _resolver_contains_forbidden_exact_key(payload: Any) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_EXACT_RAW_PATH_KEYS:
                return True
            if _resolver_contains_forbidden_exact_key(value):
                return True
    if isinstance(payload, list):
        return any(_resolver_contains_forbidden_exact_key(item) for item in payload)
    return False


def _resolver_payload_contains_value(payload: Any, raw_values: set[str]) -> bool:
    if not raw_values:
        return False
    if isinstance(payload, str):
        return payload in raw_values
    if isinstance(payload, dict):
        return any(_resolver_payload_contains_value(value, raw_values) for value in payload.values())
    if isinstance(payload, list):
        return any(_resolver_payload_contains_value(item, raw_values) for item in payload)
    return False


def _resolver_collect_raw_path_values(payload: Any) -> set[str]:
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


def _resolver_path_safety_summary(*, contract_found: bool, workbook_ref_found: bool, metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy": "safe_workbook_path_resolver_dry_run_v1",
        "status": "metadata_only_blocked",
        "contract_found": bool(contract_found),
        "workbook_ref_found": bool(workbook_ref_found),
        "raw_saved_path_present": bool(metadata.get("raw_saved_path_present")),
        "path_like_metadata_present": bool(metadata.get("path_like_metadata_present")),
        "raw_path_values_returned": False,
        "forbidden_exact_path_keys_returned": False,
        "filesystem_checked": False,
        "workbook_filesystem_checked": False,
        "path_resolved": False,
        "workbook_opened": False,
        "workbook_read": False,
    }


def evaluate_safe_workbook_path_resolver_dry_run(
    *,
    conversation_id: str,
    client_event_id: str | None = None,
    contract: Any | None = None,
) -> dict[str, Any]:
    """Evaluate workbook path readiness from contract metadata only.

    This function deliberately does not resolve, stat, open, parse, or read the
    workbook file. It only inspects already-stored Jarvis contract metadata and
    returns a public scrubbed readiness summary for a future workbook access
    alpha.
    """
    contract_payload = _resolver_contract_payload(contract)
    contract_found = contract_payload is not None
    workbook_ref = contract_payload.get("workbook_ref") if contract_payload else None
    workbook_ref_found = isinstance(workbook_ref, dict) and bool(workbook_ref)
    metadata = _resolver_detect_path_metadata(workbook_ref or {})
    raw_values = _resolver_collect_raw_path_values(workbook_ref or {})

    blocked_by_policy = [
        "metadata_only_dry_run",
        "workbook_filesystem_check_disabled",
        "workbook_open_disabled",
        "workbook_read_disabled",
        "execution_kill_switch",
    ]
    if not contract_found:
        reason = "engine_contract_not_found"
        blocked_by_policy.append("engine_contract_not_found")
    elif not workbook_ref_found:
        reason = "workbook_ref_not_found"
        blocked_by_policy.append("workbook_ref_not_found")
    else:
        reason = "safe_workbook_path_resolver_dry_run_only"

    response = {
        "conversation_id": conversation_id,
        "client_event_id": client_event_id,
        "contract_id": contract_payload.get("contract_id") if contract_payload else None,
        "route": "builder_safe_workbook_path_resolver_dry_run",
        "message": "Safe workbook path resolver dry run evaluated metadata only. No workbook path was resolved, no filesystem check was performed, and no workbook was opened or read.",
        "metadata_only": True,
        "execution_enabled": False,
        "blocked": True,
        "reason": reason,
        "contract_found": contract_found,
        "workbook_ref_found": workbook_ref_found,
        "workbook_ref_summary": _resolver_public_workbook_ref_summary(workbook_ref),
        "jarvis_metadata_store_read": contract_found,
        "path_resolved": False,
        "filesystem_checked": False,
        "workbook_filesystem_checked": False,
        "workbook_opened": False,
        "raw_saved_path_present": bool(metadata.get("raw_saved_path_present")),
        "path_like_metadata_present": bool(metadata.get("path_like_metadata_present")),
        "raw_path_value_returned": False,
        "forbidden_path_key_returned": False,
        "raw_path_returned": False,
        "raw_path_like_key_returned": False,
        "filesystem_check_required_later": True,
        "would_require_attachment_root_check_later": True,
        "blocked_by_policy": blocked_by_policy,
        "path_safety_summary": _resolver_path_safety_summary(
            contract_found=contract_found,
            workbook_ref_found=workbook_ref_found,
            metadata=metadata,
        ),
        "future_required_checks": [
            "attachment_id_must_resolve_inside_jarvis_attachment_store",
            "resolved_path_must_remain_under_approved_attachment_root",
            "extension_and_content_type_must_pass_whitelist",
            "read_approval_must_match_current_contract_and_preflight",
        ],
        **NO_ENGINE_SAFETY,
        "safety": {
            **dict(NO_ENGINE_SAFETY),
            "metadata_only": True,
            "execution_enabled": False,
            "path_resolved": False,
            "filesystem_checked": False,
            "workbook_filesystem_checked": False,
            "workbook_opened": False,
            "raw_path_value_returned": False,
            "forbidden_path_key_returned": False,
        },
        "next_safe_action": "Keep workbook open/read disabled. Use this dry-run output to verify metadata readiness before any future workbook access alpha.",
    }
    response["forbidden_path_key_returned"] = _resolver_contains_forbidden_exact_key(response)
    response["raw_path_like_key_returned"] = response["forbidden_path_key_returned"]
    response["raw_path_value_returned"] = _resolver_payload_contains_value(response, raw_values)
    response["raw_path_returned"] = response["raw_path_value_returned"]
    response["path_safety_summary"]["forbidden_exact_path_keys_returned"] = response["forbidden_path_key_returned"]
    response["path_safety_summary"]["raw_path_values_returned"] = response["raw_path_value_returned"]
    response["safety"]["forbidden_path_key_returned"] = response["forbidden_path_key_returned"]
    response["safety"]["raw_path_value_returned"] = response["raw_path_value_returned"]
    return response
