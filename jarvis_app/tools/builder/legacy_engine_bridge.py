from __future__ import annotations

import uuid
from typing import Any
from datetime import datetime, timezone

from jarvis_v5.config import (
    BUILDER_ENGINE_EXECUTION_ENABLED,
    LEGACY_BUILDER_CALLABLE,
    WORKBOOK_READ_ENABLED,
    EXCEL_OUTPUT_ENABLED,
)

CONTRACT_SCHEMA_VERSION = "builder_contract_v1"
LEGACY_TARGET = "legacy_builder_v4_contract_v1"
NO_ENGINE_SAFETY = {
    "workbook_read": False,
    "engine_called": False,
    "excel_created": False,
    "contract_only": True,
    "legacy_builder_called": False,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_execution_request_id() -> str:
    return f"exec_req_{uuid.uuid4().hex}"


def execution_lock_status() -> dict[str, Any]:
    return {
        "builder_engine_execution_enabled": bool(BUILDER_ENGINE_EXECUTION_ENABLED),
        "legacy_builder_callable": bool(LEGACY_BUILDER_CALLABLE),
        "workbook_read_enabled": bool(WORKBOOK_READ_ENABLED),
        "excel_output_enabled": bool(EXCEL_OUTPUT_ENABLED),
    }


def _preflight_ready(preflight: dict[str, Any] | None) -> bool:
    if not preflight:
        return False
    return (
        preflight.get("route") == "builder_engine_preflight_ready"
        and preflight.get("preflight_status") == "ready_for_future_engine_adapter"
        and bool((preflight.get("compatibility") or {}).get("valid"))
    )


def prepare_legacy_builder_execution_request(
    *,
    conversation_id: str,
    contract: Any | None,
    preflight: dict[str, Any] | None,
    pending_clarification: bool = False,
) -> dict[str, Any]:
    """Return an alpha.17 blocked execution report.

    This function deliberately does not import the legacy Builder runtime, open a
    workbook, create formulas, or write Excel. It only validates that the future
    execution bridge remains locked by configuration.
    """
    contract_id = getattr(contract, "contract_id", None) if contract is not None else None
    preflight_id = preflight.get("preflight_id") if preflight else None
    execution_request_id = new_execution_request_id()

    if pending_clarification:
        reason = "pending_clarification_exists"
        message = "Builder engine execution request blocked because a clarification is still open. Resolve or cancel it first."
    elif contract is None:
        reason = "engine_contract_not_found"
        message = "Builder engine execution request blocked because no ready engine contract was found."
    elif preflight is None:
        reason = "engine_preflight_not_found"
        message = "Builder engine execution request blocked because no ready engine preflight was found."
    elif not _preflight_ready(preflight):
        reason = "engine_preflight_not_ready"
        message = "Builder engine execution request blocked because the latest engine preflight is not ready."
    elif not BUILDER_ENGINE_EXECUTION_ENABLED:
        reason = "engine_execution_disabled_by_kill_switch"
        message = "Builder engine execution is disabled by kill switch. No Builder engine was called and no Excel file was created."
    else:
        # Defensive: alpha.17 should never reach this in normal packaged builds.
        reason = "engine_execution_disabled_by_alpha17_policy"
        message = "Builder engine execution is disabled in alpha.17."

    would_call = {
        "legacy_target": getattr(contract, "legacy_target", LEGACY_TARGET) if contract is not None else LEGACY_TARGET,
        "contract_schema_version": getattr(contract, "contract_schema_version", CONTRACT_SCHEMA_VERSION) if contract is not None else CONTRACT_SCHEMA_VERSION,
        "contract_id": contract_id,
        "preflight_id": preflight_id,
        "legacy_entrypoint": "legacy_builder_v4_contract_v1",
    }

    compatibility = {
        "valid": False,
        "score": 0,
        "missing_required_fields": [],
        "ambiguous_fields": [],
        "warnings": [],
        "issues": [reason],
    }
    if reason == "engine_contract_not_found":
        compatibility["missing_required_fields"] = ["engine_contract"]
    elif reason == "engine_preflight_not_found":
        compatibility["missing_required_fields"] = ["engine_preflight"]
    elif reason == "engine_preflight_not_ready":
        compatibility["missing_required_fields"] = ["ready_engine_preflight"]

    return {
        "conversation_id": conversation_id,
        "execution_request_id": execution_request_id,
        "contract_id": contract_id,
        "preflight_id": preflight_id,
        "route": "builder_engine_execution_blocked",
        "message": message,
        "blocked": True,
        "reason": reason,
        "execution_status": "disabled",
        "bridge_status": "blocked_by_kill_switch" if reason == "engine_execution_disabled_by_kill_switch" else "blocked",
        "execution_enabled": False,
        "legacy_target": would_call["legacy_target"],
        "contract_schema_version": would_call["contract_schema_version"],
        "would_call": would_call,
        "compatibility": compatibility,
        "safety": dict(NO_ENGINE_SAFETY),
        "execution_locks": execution_lock_status(),
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
        "validation": {"valid": False, "issues": [reason], "warnings": []},
        "created_at": now_iso(),
    }


def execution_summary(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {
            "found": False,
            "status": "not_requested",
            "execution_enabled": False,
            "next_action": "Engine execution is disabled in alpha.17.",
            **NO_ENGINE_SAFETY,
        }
    safety = payload.get("safety") or NO_ENGINE_SAFETY
    return {
        "found": True,
        "execution_request_id": payload.get("execution_request_id"),
        "status": payload.get("bridge_status") or payload.get("execution_status"),
        "execution_status": payload.get("execution_status"),
        "execution_enabled": False,
        "reason": payload.get("reason"),
        "contract_id": payload.get("contract_id"),
        "preflight_id": payload.get("preflight_id"),
        "legacy_target": payload.get("legacy_target"),
        "contract_schema_version": payload.get("contract_schema_version"),
        "workbook_read": bool(safety.get("workbook_read", False)),
        "engine_called": bool(safety.get("engine_called", False)),
        "excel_created": bool(safety.get("excel_created", False)),
        "contract_only": bool(safety.get("contract_only", True)),
        "legacy_builder_called": bool(safety.get("legacy_builder_called", False)),
    }
