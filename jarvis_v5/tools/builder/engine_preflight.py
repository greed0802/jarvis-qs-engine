from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

from jarvis_v5.config import PACKAGE_ROOT
from jarvis_v5.schemas.builder_engine_contract_schema import BuilderEngineContract
from jarvis_v5.tools.builder.engine_boundary_audit import audit_builder_engine_boundary, boundary_audit_summary

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


def new_preflight_id() -> str:
    return f"preflight_{uuid.uuid4().hex}"


def _contract_missing_fields(contract: BuilderEngineContract) -> list[str]:
    missing: list[str] = []
    setup = contract.builder_setup
    checks = {
        "workbook_ref": contract.workbook_ref,
        "trade_profile": setup.trade_profile,
        "costx_function": setup.costx_function,
        "unit": setup.unit,
        "dynamic_zones": setup.dynamic_zones,
        "heading_assignments": setup.heading_assignments,
        "levels": setup.levels,
    }
    if setup.costx_function == "XGETCUSTOM":
        checks["custom_quantity"] = setup.custom_quantity
    for field, value in checks.items():
        if value in (None, "", [], {}):
            missing.append(field)
    return missing


def _frozen_contract_fixture_payload(contract: BuilderEngineContract) -> dict[str, Any]:
    """Create a regression fixture from contract metadata only.

    This deliberately excludes workbook contents and source file bytes. It keeps
    only workbook metadata and the frozen contract shape required for future
    adapter compatibility tests.
    """
    payload = contract.model_dump(mode="json")
    return {
        "fixture_schema": "builder_engine_contract_fixture_v1",
        "created_at": now_iso(),
        "contract_schema_version": contract.contract_schema_version,
        "legacy_target": contract.legacy_target,
        "contract_hash": contract.contract_hash,
        "safety": dict(NO_ENGINE_SAFETY),
        "contract": payload,
    }


def write_frozen_contract_fixture(contract: BuilderEngineContract) -> str:
    fixtures_dir = PACKAGE_ROOT / "tests" / "fixtures" / "contracts"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    setup = contract.builder_setup
    trade = (setup.trade_profile or "trade").lower().replace(" / ", "_").replace(" ", "_")
    func = (setup.costx_function or "function").lower()
    # Keep the known golden filename stable for the main Wall Types flow.
    if setup.trade_profile == "Wall Types" and setup.costx_function == "XGETWALLAREA":
        name = "wall_types_xgetwallarea_zone1_head2_gf_l3_contract_v1.json"
    else:
        name = f"{trade}_{func}_contract_v1.json"
    path = fixtures_dir / name
    path.write_text(json.dumps(_frozen_contract_fixture_payload(contract), indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path.relative_to(PACKAGE_ROOT.parent))


def run_engine_preflight(contract: BuilderEngineContract | None, *, export_fixture: bool = True) -> dict[str, Any]:
    if not contract:
        return {
            "preflight_id": None,
            "route": "builder_engine_preflight_blocked",
            "blocked": True,
            "reason": "engine_contract_not_found",
            "preflight_status": "blocked",
            "contract_id": None,
            "contract_schema_version": CONTRACT_SCHEMA_VERSION,
            "legacy_target": LEGACY_TARGET,
            "compatibility": {
                "valid": False,
                "score": 0,
                "missing_required_fields": ["engine_contract"],
                "ambiguous_fields": [],
                "warnings": [],
            },
            "safety": dict(NO_ENGINE_SAFETY),
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "contract_only": True,
            "legacy_builder_called": False,
            "engine_boundary_audit": boundary_audit_summary(None),
            "validation": {"valid": False, "issues": ["engine_contract_not_found"], "warnings": []},
            "message": "Builder engine preflight blocked because no ready engine contract was found.",
        }

    audit = audit_builder_engine_boundary(contract)
    missing = _contract_missing_fields(contract)
    ambiguous: list[str] = []
    warnings: list[str] = []
    issues: list[str] = []

    if contract.contract_status != "ready_for_engine_connection":
        issues.append("contract_not_ready_or_stale")
    if contract.contract_schema_version != CONTRACT_SCHEMA_VERSION:
        issues.append("unsupported_contract_schema_version")
    if contract.legacy_target != LEGACY_TARGET:
        issues.append("unsupported_legacy_target")
    if not contract.validation.valid:
        issues.extend([item for item in contract.validation.issues if item not in issues])
    if audit.get("blocked") or audit.get("missing_legacy_required_fields"):
        issues.append("boundary_audit_not_compatible")
        for field in audit.get("missing_legacy_required_fields") or []:
            if field not in missing:
                missing.append(field)
    safety = dict(NO_ENGINE_SAFETY)
    actual_safety = contract.safety.model_dump(mode="json")
    for key in ["workbook_read", "engine_called", "excel_created", "legacy_builder_called"]:
        if actual_safety.get(key):
            issues.append(f"safety_violation_{key}")
    if not actual_safety.get("contract_only", True):
        issues.append("safety_violation_contract_only")

    valid = not issues and not missing and not ambiguous
    score = 100 if valid else max(0, 100 - (len(issues) * 20) - (len(missing) * 10) - (len(ambiguous) * 10))
    preflight_id = new_preflight_id()
    fixture_path = write_frozen_contract_fixture(contract) if valid and export_fixture else None
    route = "builder_engine_preflight_ready" if valid else "builder_engine_preflight_blocked"
    reason = None if valid else (issues[0] if issues else "missing_required_fields")
    status = "ready_for_future_engine_adapter" if valid else "blocked"

    return {
        "preflight_id": preflight_id,
        "route": route,
        "blocked": not valid,
        "reason": reason,
        "preflight_status": status,
        "contract_id": contract.contract_id,
        "contract_schema_version": contract.contract_schema_version,
        "legacy_target": contract.legacy_target,
        "compatibility": {
            "valid": valid,
            "score": score,
            "missing_required_fields": missing,
            "ambiguous_fields": ambiguous,
            "warnings": warnings,
            "issues": issues,
        },
        "safety": safety,
        "fixture_path": fixture_path,
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
        "contract": contract.model_dump(mode="json"),
        "engine_boundary_audit": boundary_audit_summary(contract),
        "validation": {"valid": valid, "issues": issues, "warnings": warnings},
        "message": (
            "Builder engine preflight passed. No Builder engine was called and no Excel file was created."
            if valid else
            "Builder engine preflight blocked. No Builder engine was called and no Excel file was created."
        ),
        "created_at": now_iso(),
    }


def preflight_summary(preflight: dict[str, Any] | None) -> dict[str, Any]:
    if not preflight:
        return {
            "found": False,
            "status": "not_run",
            "next_action": "Create engine contract, then run preflight.",
            **NO_ENGINE_SAFETY,
        }
    compatibility = preflight.get("compatibility") or {}
    safety = preflight.get("safety") or NO_ENGINE_SAFETY
    return {
        "found": True,
        "preflight_id": preflight.get("preflight_id"),
        "status": preflight.get("preflight_status"),
        "contract_id": preflight.get("contract_id"),
        "contract_schema_version": preflight.get("contract_schema_version"),
        "legacy_target": preflight.get("legacy_target"),
        "compatibility_score": compatibility.get("score"),
        "missing_required_fields": compatibility.get("missing_required_fields") or [],
        "ambiguous_fields": compatibility.get("ambiguous_fields") or [],
        "warnings": compatibility.get("warnings") or [],
        "fixture_path": preflight.get("fixture_path"),
        "workbook_read": bool(safety.get("workbook_read", False)),
        "engine_called": bool(safety.get("engine_called", False)),
        "excel_created": bool(safety.get("excel_created", False)),
        "contract_only": bool(safety.get("contract_only", True)),
        "legacy_builder_called": bool(safety.get("legacy_builder_called", False)),
    }
