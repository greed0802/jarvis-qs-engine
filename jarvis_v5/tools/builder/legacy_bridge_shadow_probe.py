from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from jarvis_v5.config import (
    PACKAGE_ROOT,
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

LEGACY_BRIDGE_STUB_PATH = PACKAGE_ROOT / "tools" / "builder" / "legacy_engine_bridge.py"
REQUIRED_CONTRACT_SETUP_FIELDS = [
    "workbook_ref",
    "trade_profile",
    "costx_function",
    "unit",
    "dynamic_zones",
    "heading_assignments",
    "levels",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_probe_id() -> str:
    return f"legacy_bridge_probe_{uuid.uuid4().hex}"


def _contract_payload(contract: Any | None) -> dict[str, Any] | None:
    if contract is None:
        return None
    if hasattr(contract, "model_dump"):
        return contract.model_dump(mode="json")
    if isinstance(contract, dict):
        return contract
    return None


def _contract_validation_ready(contract: Any | None, payload: dict[str, Any] | None) -> bool:
    if contract is None or payload is None:
        return False
    validation = payload.get("validation") or {}
    if isinstance(validation, dict) and validation.get("valid") is False:
        return False
    status = payload.get("contract_status") or getattr(contract, "contract_status", None)
    if status and status != "ready_for_engine_connection":
        return False
    setup = payload.get("builder_setup") or payload.get("contract", {}).get("builder_setup") or {}
    # Current contract shape stores setup at contract.builder_setup.
    if not setup and hasattr(contract, "builder_setup"):
        setup_obj = getattr(contract, "builder_setup")
        setup = setup_obj.model_dump(mode="json") if hasattr(setup_obj, "model_dump") else setup_obj
    return bool(setup)


def _missing_contract_fields(payload: dict[str, Any] | None) -> list[str]:
    if not payload:
        return ["engine_contract"]
    setup = payload.get("builder_setup") or {}
    missing: list[str] = []
    workbook_ref = payload.get("workbook_ref") or setup.get("workbook_ref")
    if not workbook_ref:
        missing.append("workbook_ref")
    for field in ["trade_profile", "costx_function", "unit"]:
        if not setup.get(field):
            missing.append(field)
    for field in ["dynamic_zones", "heading_assignments", "levels"]:
        value = setup.get(field)
        if not value:
            missing.append(field)
    if setup.get("costx_function") == "XGETCUSTOM" and not setup.get("custom_quantity"):
        missing.append("custom_quantity")
    return missing


def _blocked_by_policy() -> list[str]:
    blocked: list[str] = []
    if not WORKBOOK_READ_ENABLED:
        blocked.append("workbook_read_disabled")
    if not LEGACY_BUILDER_CALLABLE:
        blocked.append("legacy_builder_callable_disabled")
    if not EXCEL_OUTPUT_ENABLED:
        blocked.append("excel_output_disabled")
    if not BUILDER_ENGINE_EXECUTION_ENABLED:
        blocked.append("execution_kill_switch")
    return blocked


def run_legacy_bridge_shadow_probe(
    *,
    conversation_id: str,
    client_event_id: str | None = None,
    contract: Any | None = None,
    allow_missing_contract: bool = True,
) -> dict[str, Any]:
    """Inspect the future legacy Builder bridge boundary without execution.

    This owner is metadata-only. It does not import the real legacy Builder,
    does not open workbook files, does not generate formulas, and does not
    create Excel. It only reports whether the current v5 contract metadata is
    structurally ready for a future mapping discussion while execution remains
    blocked by policy.
    """
    contract_payload = _contract_payload(contract)
    contract_found = contract_payload is not None
    contract_ready = _contract_validation_ready(contract, contract_payload)
    missing_fields = [] if contract_ready else _missing_contract_fields(contract_payload)
    blocked_by_policy = _blocked_by_policy()
    bridge_layer_found = LEGACY_BRIDGE_STUB_PATH.exists()
    safe_for_future_mapping = bool(bridge_layer_found and (contract_ready or allow_missing_contract))
    safe_for_execution = False

    reason = "legacy_builder_execution_disabled"
    if not contract_found and not allow_missing_contract:
        reason = "engine_contract_not_found"
    elif contract_found and not contract_ready:
        reason = "engine_contract_not_ready"

    return {
        "conversation_id": conversation_id,
        "client_event_id": client_event_id,
        "probe_id": new_probe_id(),
        "route": "builder_legacy_bridge_shadow_probe",
        "metadata_only": True,
        "execution_enabled": False,
        "blocked": True,
        "reason": reason,
        "message": "Legacy Builder bridge shadow probe completed. No workbook was read, no legacy Builder was imported or called, and no Excel file was created.",
        **NO_ENGINE_SAFETY,
        "safety": dict(NO_ENGINE_SAFETY),
        "bridge_probe": {
            "bridge_layer_found": bridge_layer_found,
            "bridge_layer_path": "jarvis_v5/tools/builder/legacy_engine_bridge.py" if bridge_layer_found else None,
            "bridge_layer_status": "stub_only" if bridge_layer_found else "missing",
            "legacy_import_attempted": False,
            "legacy_module_imported": False,
            "legacy_callable_available": False,
            "legacy_builder_called": False,
            "contract_found": contract_found,
            "contract_id": getattr(contract, "contract_id", None) if contract is not None else None,
            "contract_ready": contract_ready,
            "safe_for_future_mapping": safe_for_future_mapping,
            "safe_for_execution": safe_for_execution,
            "missing_contract_fields": missing_fields,
        },
        "execution_locks": {
            "builder_engine_execution_enabled": bool(BUILDER_ENGINE_EXECUTION_ENABLED),
            "legacy_builder_callable": bool(LEGACY_BUILDER_CALLABLE),
            "workbook_read_enabled": bool(WORKBOOK_READ_ENABLED),
            "excel_output_enabled": bool(EXCEL_OUTPUT_ENABLED),
        },
        "blocked_by_policy": blocked_by_policy,
        "next_safe_action": "Keep execution disabled. Resolve missing contract fields before any future isolated bridge mapping test." if missing_fields else "Keep execution disabled. Future bridge mapping can be reviewed against this contract metadata.",
        "contract_schema_version": getattr(contract, "contract_schema_version", None) if contract is not None else None,
        "legacy_target": getattr(contract, "legacy_target", "legacy_builder_v4_contract_v1"),
        "contract": contract_payload,
        "created_at": now_iso(),
    }
