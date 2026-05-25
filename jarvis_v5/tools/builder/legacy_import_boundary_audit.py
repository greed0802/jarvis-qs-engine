from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from jarvis_v5.config import (
    APP_VERSION,
    PACKAGE_ROOT,
    LEGACY_IMPORT_AUDITS_DIR,
    BUILDER_ENGINE_EXECUTION_ENABLED,
    LEGACY_BUILDER_CALLABLE,
    WORKBOOK_READ_ENABLED,
    EXCEL_OUTPUT_ENABLED,
)
from jarvis_v5.core.json_store import write_json, read_json

NO_ENGINE_SAFETY = {
    "workbook_read": False,
    "engine_called": False,
    "excel_created": False,
    "contract_only": True,
    "legacy_builder_called": False,
}

RISK_PATTERNS = {
    "legacy_runtime_imports": [
        "legacy_builder_runtime",
        "from legacy_builder",
        "import legacy_builder",
        "from builder_legacy",
        "import builder_legacy",
    ],
    "dynamic_import_patterns": [
        "importlib.import_module",
        "__import__(",
    ],
    "subprocess_execution_patterns": [
        "subprocess.",
        "os.system(",
    ],
    "workbook_reader_imports": [
        "openpyxl.load_workbook",
        "pandas.read_excel",
        "pd.read_excel",
    ],
    "legacy_builder_call_patterns": [
        "create_builder_output(",
        "run_legacy_builder(",
        "legacy_builder_callable(",
    ],
}

IGNORED_SCAN_FILES = {
    "legacy_import_boundary_audit.py",  # contains pattern names for reporting only
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_audit_id() -> str:
    return f"legacy_audit_{uuid.uuid4().hex}"


def _safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(PACKAGE_ROOT))
    except Exception:
        return str(path)


def _scan_source_text() -> dict[str, list[dict[str, Any]]]:
    """Static text scan of Jarvis v5 source only.

    This does not import legacy Builder, does not execute scanned code, does not
    read workbooks, and does not create Excel. Findings are diagnostic only.
    """
    findings: dict[str, list[dict[str, Any]]] = {key: [] for key in RISK_PATTERNS}
    for path in PACKAGE_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        if path.name in IGNORED_SCAN_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for group, patterns in RISK_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    findings[group].append({
                        "file": _safe_rel(path),
                        "pattern": pattern,
                        "diagnostic_only": True,
                    })
    return findings


def _summary_findings(findings: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    # Alpha.20 reports diagnostics but never treats source-text mentions as runtime execution.
    return {
        "legacy_runtime_imports_found": findings.get("legacy_runtime_imports", []),
        "dynamic_import_patterns_found": findings.get("dynamic_import_patterns", []),
        "subprocess_execution_patterns_found": findings.get("subprocess_execution_patterns", []),
        "workbook_reader_imports_found": findings.get("workbook_reader_imports", []),
        "legacy_builder_call_patterns_found": findings.get("legacy_builder_call_patterns", []),
        "diagnostic_only": True,
    }


def run_legacy_import_boundary_audit(
    *,
    conversation_id: str,
    client_event_id: str | None = None,
    write_report: bool = True,
) -> dict[str, Any]:
    """Return a no-call audit for the future legacy Builder import boundary."""
    audit_id = new_audit_id()
    findings = _scan_source_text()
    payload: dict[str, Any] = {
        "audit_id": audit_id,
        "conversation_id": conversation_id,
        "client_event_id": client_event_id,
        "route": "builder_legacy_import_boundary_audit",
        "blocked": False,
        "audit_status": "locked_no_import",
        "reason": "legacy_import_boundary_locked",
        "version": APP_VERSION,
        "legacy_import_attempted": False,
        "legacy_module_imported": False,
        "legacy_builder_callable": bool(LEGACY_BUILDER_CALLABLE),
        "legacy_builder_called": False,
        "builder_engine_execution_enabled": bool(BUILDER_ENGINE_EXECUTION_ENABLED),
        "workbook_read_enabled": bool(WORKBOOK_READ_ENABLED),
        "excel_output_enabled": bool(EXCEL_OUTPUT_ENABLED),
        "dynamic_import_allowed": False,
        "subprocess_allowed": False,
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "safety": dict(NO_ENGINE_SAFETY),
        "import_boundary": {
            "policy": "no_legacy_import_allowed",
            "legacy_import_attempted": False,
            "legacy_module_imported": False,
            "legacy_builder_callable": bool(LEGACY_BUILDER_CALLABLE),
            "legacy_builder_called": False,
            "dynamic_import_allowed": False,
            "subprocess_allowed": False,
            "workbook_read_allowed": bool(WORKBOOK_READ_ENABLED),
            "excel_output_allowed": bool(EXCEL_OUTPUT_ENABLED),
        },
        "bridge_stub": {
            "module": "jarvis_v5.tools.builder.legacy_engine_bridge",
            "status": "stub_only",
            "can_prepare_blocked_request": True,
            "can_execute": False,
            "legacy_runtime_imported": False,
        },
        "locks": {
            "builder_engine_execution_enabled": bool(BUILDER_ENGINE_EXECUTION_ENABLED),
            "legacy_builder_callable": bool(LEGACY_BUILDER_CALLABLE),
            "workbook_read_enabled": bool(WORKBOOK_READ_ENABLED),
            "excel_output_enabled": bool(EXCEL_OUTPUT_ENABLED),
        },
        "static_findings": _summary_findings(findings),
        "future_connection_requirements": [
            "Explicit FIRE approval",
            "Dedicated legacy adapter module",
            "Static contract-to-legacy mapping",
            "Preflight must pass",
            "Execution kill switch must remain default false",
            "Workbook read must remain disabled until approved separately",
        ],
        "message": "Legacy Builder import boundary audit completed. No legacy Builder module was imported or called.",
        "created_at": now_iso(),
    }
    if write_report:
        LEGACY_IMPORT_AUDITS_DIR.mkdir(parents=True, exist_ok=True)
        write_json(LEGACY_IMPORT_AUDITS_DIR / f"{audit_id}.json", payload)
        write_json(LEGACY_IMPORT_AUDITS_DIR / f"latest_{conversation_id.replace('/', '_')}.json", payload)
    return payload


def latest_legacy_import_boundary_audit_summary(conversation_id: str) -> dict[str, Any]:
    path = LEGACY_IMPORT_AUDITS_DIR / f"latest_{conversation_id.replace('/', '_')}.json"
    data = read_json(path, default=None)
    if not data:
        return {"found": False}
    return {
        "found": True,
        "audit_id": data.get("audit_id"),
        "audit_status": data.get("audit_status"),
        "legacy_import_attempted": bool(data.get("legacy_import_attempted", False)),
        "legacy_module_imported": bool(data.get("legacy_module_imported", False)),
        "legacy_builder_callable": bool(data.get("legacy_builder_callable", False)),
        "legacy_builder_called": bool(data.get("legacy_builder_called", False)),
        "builder_engine_execution_enabled": bool(data.get("builder_engine_execution_enabled", False)),
        "workbook_read_enabled": bool(data.get("workbook_read_enabled", False)),
        "excel_output_enabled": bool(data.get("excel_output_enabled", False)),
        "workbook_read": bool(data.get("workbook_read", False)),
        "engine_called": bool(data.get("engine_called", False)),
        "excel_created": bool(data.get("excel_created", False)),
        "contract_only": bool(data.get("contract_only", True)),
        "legacy_import_boundary_audit_url": f"/api/builder/legacy-import-boundary-audit/latest/{conversation_id}",
    }


def latest_legacy_import_boundary_audit(conversation_id: str) -> dict[str, Any]:
    path = LEGACY_IMPORT_AUDITS_DIR / f"latest_{conversation_id.replace('/', '_')}.json"
    data = read_json(path, default=None)
    if not data:
        return {
            "found": False,
            "route": "builder_legacy_import_boundary_audit_latest_not_found",
            "conversation_id": conversation_id,
            **NO_ENGINE_SAFETY,
            "safety": dict(NO_ENGINE_SAFETY),
        }
    data = dict(data)
    data["found"] = True
    data["route"] = "builder_legacy_import_boundary_audit_latest"
    return data
