from __future__ import annotations

from typing import Any

from jarvis_v5.schemas.builder_engine_contract_schema import BuilderEngineContract

CONTRACT_SCHEMA_VERSION = "builder_contract_v1"
LEGACY_TARGET = "legacy_builder_v4_contract_v1"

LEGACY_REQUIRED_MAPPINGS: dict[str, dict[str, str]] = {
    "workbook_ref": {
        "contract_path": "$.contract.workbook_ref",
        "legacy_field": "workbook_ref",
    },
    "trade_profile": {
        "contract_path": "$.contract.builder_setup.trade_profile",
        "legacy_field": "trade_profile",
    },
    "costx_function": {
        "contract_path": "$.contract.builder_setup.costx_function",
        "legacy_field": "selected_function",
    },
    "unit": {
        "contract_path": "$.contract.builder_setup.unit",
        "legacy_field": "unit",
    },
    "dynamic_zones": {
        "contract_path": "$.contract.builder_setup.dynamic_zones",
        "legacy_field": "dynamic_zones",
    },
    "heading_assignments": {
        "contract_path": "$.contract.builder_setup.heading_assignments",
        "legacy_field": "heading_assignments",
    },
    "levels": {
        "contract_path": "$.contract.builder_setup.levels",
        "legacy_field": "levels",
    },
}

LEGACY_OPTIONAL_MAPPINGS: dict[str, dict[str, str]] = {
    "custom_quantity": {
        "contract_path": "$.contract.builder_setup.custom_quantity",
        "legacy_field": "custom_quantity",
    },
    "aliases": {
        "contract_path": "$.contract.builder_setup.aliases",
        "legacy_field": "aliases",
    },
    "item_code_settings": {
        "contract_path": "$.contract.builder_setup.item_code_settings",
        "legacy_field": "item_code_settings",
    },
    "zone_mode": {
        "contract_path": "$.contract.builder_setup.zone_mode",
        "legacy_field": "zone_mode",
    },
    "trade_registry": {
        "contract_path": "$.contract.builder_setup.trade_registry",
        "legacy_field": "trade_registry",
    },
}


def _is_missing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _map_entry(name: str, mapping: dict[str, str], value: Any, *, optional: bool = False) -> dict[str, Any]:
    status = "mapped_optional" if optional else "mapped"
    if _is_missing(value):
        status = "missing_optional" if optional else "missing_required"
    return {
        "contract_field": name,
        "contract_path": mapping["contract_path"],
        "legacy_field": mapping["legacy_field"],
        "status": status,
        "present": not _is_missing(value),
    }


def audit_builder_engine_boundary(contract: BuilderEngineContract | None) -> dict[str, Any]:
    """Inspect a saved Builder engine contract without calling any engine.

    Alpha.13 is a pure boundary audit. It reports how the saved contract would map
    to the future legacy Builder input shape, but deliberately does not read a
    workbook, generate formulas, create preview rows, create Excel, or call legacy
    Builder code.
    """
    base: dict[str, Any] = {
        "found": bool(contract),
        "route": "builder_engine_boundary_audit" if contract else "builder_engine_boundary_audit_blocked",
        "blocked": not bool(contract),
        "audit_status": "not_ready" if not contract else "not_started",
        "reason": None if contract else "contract_not_found",
        "contract_id": contract.contract_id if contract else None,
        "contract_schema_version": CONTRACT_SCHEMA_VERSION,
        "legacy_target": LEGACY_TARGET,
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
        "mapping": {},
        "unmapped_contract_fields": [],
        "missing_legacy_required_fields": [],
        "warnings": [],
        "validation": {"valid": False, "issues": ["contract_not_found"] if not contract else [], "warnings": []},
    }
    if contract is None:
        base["message"] = "Builder engine boundary audit blocked because no saved contract was found."
        return base

    setup = contract.builder_setup
    values: dict[str, Any] = {
        "workbook_ref": contract.workbook_ref,
        "trade_profile": setup.trade_profile,
        "costx_function": setup.costx_function,
        "unit": setup.unit,
        "dynamic_zones": setup.dynamic_zones,
        "heading_assignments": setup.heading_assignments,
        "levels": setup.levels,
        "custom_quantity": setup.custom_quantity,
        "aliases": setup.aliases,
        "item_code_settings": setup.item_code_settings,
        "zone_mode": setup.zone_mode,
        "trade_registry": getattr(setup, "trade_registry", None),
    }

    mapping: dict[str, Any] = {}
    missing_required: list[str] = []
    for name, info in LEGACY_REQUIRED_MAPPINGS.items():
        entry = _map_entry(name, info, values.get(name), optional=False)
        mapping[name] = entry
        if entry["status"] == "missing_required":
            missing_required.append(info["legacy_field"])
    for name, info in LEGACY_OPTIONAL_MAPPINGS.items():
        mapping[name] = _map_entry(name, info, values.get(name), optional=True)

    issues: list[str] = []
    warnings: list[str] = []
    blockers: list[dict[str, Any]] = []

    if contract.contract_status != "ready_for_engine_connection":
        issues.append("contract_not_ready")
        blockers.append({"code": "contract_not_ready", "message": "Saved contract is not ready for engine connection.", "fields": ["contract_status"]})
    if not contract.validation.valid:
        issues.extend([issue for issue in contract.validation.issues if issue not in issues])
        blockers.append({"code": "contract_validation_failed", "message": "Saved contract validation is not valid.", "fields": ["validation"]})
    if missing_required:
        issues.append("missing_legacy_required_fields")
        blockers.append({"code": "missing_legacy_required_fields", "message": "Required legacy Builder input fields are missing.", "fields": missing_required})
    if not contract.safety.contract_only:
        issues.append("contract_only_false")
        blockers.append({"code": "contract_only_false", "message": "Contract safety flag contract_only must remain true.", "fields": ["contract_only"]})
    for safety_field in ["workbook_read", "engine_called", "excel_created", "legacy_builder_called"]:
        if bool(getattr(contract.safety, safety_field, False)):
            issues.append(f"{safety_field}_unexpected_true")
            blockers.append({"code": f"{safety_field}_unexpected_true", "message": f"Safety violation: {safety_field} was true.", "fields": [safety_field]})

    if mapping["custom_quantity"]["status"] == "missing_optional" and setup.costx_function == "XGETCUSTOM":
        issues.append("missing_custom_quantity")
        blockers.append({"code": "missing_custom_quantity", "message": "XGETCUSTOM requires custom quantity before any future engine call.", "fields": ["custom_quantity"]})
    elif mapping["custom_quantity"]["status"] == "missing_optional":
        warnings.append("Optional custom quantity is not set; this is acceptable unless the selected function is XGETCUSTOM.")

    audit_status = "compatible" if not issues and not warnings else "compatible_with_warnings" if not issues else "not_ready"
    base.update({
        "blocked": bool(issues),
        "audit_status": audit_status,
        "reason": None if not issues else issues[0],
        "mapping": mapping,
        "missing_legacy_required_fields": missing_required,
        "warnings": warnings,
        "validation": {
            "valid": not issues,
            "issues": issues,
            "warnings": warnings,
            "blockers": blockers,
        },
        "message": "Builder engine boundary audit completed. No Builder engine was called and no Excel file was created." if not issues else "Builder engine boundary audit found blockers. No Builder engine was called and no Excel file was created.",
    })
    return base


def boundary_audit_summary(contract: BuilderEngineContract | None) -> dict[str, Any]:
    audit = audit_builder_engine_boundary(contract)
    return {
        "found": bool(contract),
        "audit_status": audit.get("audit_status"),
        "contract_id": audit.get("contract_id"),
        "contract_schema_version": audit.get("contract_schema_version"),
        "legacy_target": audit.get("legacy_target"),
        "missing_legacy_required_fields": audit.get("missing_legacy_required_fields") or [],
        "warnings": audit.get("warnings") or [],
        "validation": audit.get("validation") or {},
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "legacy_builder_called": False,
    }
