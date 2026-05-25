from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REGISTRY_DIR = Path(__file__).resolve().parent

REGISTRY_FILES: dict[str, str] = {
    "tools": "tool_registry.json",
    "capabilities": "capability_registry.json",
    "connectors": "connector_registry.json",
    "models": "model_registry.json",
    "execution_policies": "execution_policy_registry.json",
    "requirement_advisor": "requirement_advisor_registry.json",
    "source_authorities": "source_authority_registry.json",
    "scope_advisors": "scope_advisor_registry.json",
    "file_requirements": "file_requirement_registry.json",
    "rfi_templates": "rfi_template_registry.json",
    "ecosystem_adapters": "ecosystem_adapter_registry.json",
    "voice_assistants": "voice_assistant_registry.json",
}

INDEX_FIELDS: dict[str, str] = {
    "tools": "tools",
    "capabilities": "capabilities",
    "connectors": "connectors",
    "models": "models",
    "execution_policies": "policies",
    "requirement_advisor": "requirements",
    "source_authorities": "authorities",
    "scope_advisors": "scope_advisors",
    "file_requirements": "file_requirements",
    "rfi_templates": "rfi_templates",
    "ecosystem_adapters": "ecosystem_adapters",
    "voice_assistants": "voice_assistants",
}

KEY_FIELDS: dict[str, str] = {
    "tools": "tool_key",
    "capabilities": "capability_key",
    "connectors": "connector_key",
    "models": "model_key",
    "execution_policies": "policy_key",
    "requirement_advisor": "requirement_key",
    "source_authorities": "authority_key",
    "scope_advisors": "scope_advisor_key",
    "file_requirements": "file_key",
    "rfi_templates": "template_key",
    "ecosystem_adapters": "adapter_key",
    "voice_assistants": "voice_key",
}


def registry_safety_payload() -> dict[str, Any]:
    return {
        "metadata_only": True,
        "execution_enabled": False,
        "all_entries_execution_disabled": True,
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
        "connector_called": False,
        "model_called": False,
        "install_command_run": False,
        "tool_execution_called": False,
    }


@lru_cache(maxsize=None)
def load_registry(registry_name: str) -> dict[str, Any]:
    if registry_name not in REGISTRY_FILES:
        return {
            "found": False,
            "registry": registry_name,
            "reason": "unknown_registry",
            **registry_safety_payload(),
        }
    path = REGISTRY_DIR / REGISTRY_FILES[registry_name]
    if not path.exists():
        return {
            "found": False,
            "registry": registry_name,
            "reason": "registry_file_missing",
            **registry_safety_payload(),
        }
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        data = {"items": data}
    data.setdefault("registry", registry_name)
    data.setdefault("found", True)
    data.update(registry_safety_payload())
    return data


def list_registry(registry_name: str) -> dict[str, Any]:
    data = dict(load_registry(registry_name))
    data.update(registry_safety_payload())
    return data


def registry_items(registry_name: str) -> list[dict[str, Any]]:
    data = load_registry(registry_name)
    field = INDEX_FIELDS.get(registry_name)
    items = data.get(field) if field else None
    return list(items or []) if isinstance(items, list) else []


def get_registry_item(registry_name: str, key: str) -> dict[str, Any]:
    key_field = KEY_FIELDS.get(registry_name)
    for item in registry_items(registry_name):
        if str(item.get(key_field)) == key:
            return {"found": True, "item": item, **registry_safety_payload()}
    return {"found": False, "registry": registry_name, "key": key, "reason": "item_not_found", **registry_safety_payload()}


def _norm(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _contains_any(text: str, terms: list[str]) -> bool:
    normalized = _norm(text)
    return any(term.lower() in normalized for term in terms)


RISK_ORDER = {
    "low": 1,
    "low_medium": 2,
    "medium": 3,
    "medium_high": 4,
    "high": 5,
}


def _highest_risk(matches: list[dict[str, Any]]) -> str:
    if not matches:
        return "low"
    return max((str(m.get("risk_level") or "low") for m in matches), key=lambda risk: RISK_ORDER.get(risk, 0))


def _requires_registry_approval(matches: list[dict[str, Any]]) -> bool:
    risk_level = _highest_risk(matches)
    if RISK_ORDER.get(risk_level, 0) >= RISK_ORDER["medium_high"]:
        return True
    high_control_capabilities = {
        "workbook_read_or_engine_execution_policy",
        "workbook_tool_ambiguity",
        "code_patch_worker",
        "smart_home_control",
        "remote_access_connector",
        "document_ocr_or_report_reader",
    }
    return any(
        str(m.get("capability")) in high_control_capabilities
        or str(m.get("status") or "").startswith("requires")
        or "approval" in str(m.get("status") or "")
        for m in matches
    )




def _advisory_type_for_matches(matches: list[dict[str, Any]], request_text: str) -> str:
    """Classify registry advisory responses without enabling execution.

    This is response-contract metadata only. It does not call tools, mutate
    Builder state, read workbooks, or create outputs.
    """
    text = _norm(request_text)
    capabilities = {str(m.get("capability") or "") for m in matches}
    tools = {tool for m in matches for tool in m.get("tool_candidates", [])}

    if "draft_rfi" in capabilities:
        return "rfi_template_advisory"
    if "file_requirement_advice" in capabilities or "file_requirement_advisor" in tools:
        return "file_requirement_advisory"
    if "scope_risk_checklist" in capabilities:
        return "scope_risk_advisory"
    if "qs_scope_advice" in capabilities or "qs_scope_advisor" in tools:
        if (
            "risk" in text
            or "scope risk" in text
            or "checklist from" in text
            or "report" in text
            or "missing scope" in text
        ):
            return "scope_risk_advisory"
        return "qs_scope_advisory"
    if "workbook_tool_ambiguity" in capabilities or "future_tool_advisory" in capabilities or "future_tool_advisor" in tools:
        return "capability_advisory"
    if len(tools) > 1 or _contains_any(text, ["which tool", "which capability", "what tool", "tool should", "capability should"]):
        return "capability_advisory"
    return "capability_advisory"



def _matched_scope_item(text: str) -> dict[str, Any] | None:
    """Return the first deterministic scope advisor match, if any.

    Metadata only. This never reads files or calls tools.
    """
    normalized = _norm(text)
    for item in registry_items("scope_advisors"):
        aliases = item.get("aliases") or [item.get("scope_advisor_key", "")]
        if _contains_any(normalized, aliases):
            return item
    return None


def _scope_advisory_requested(text: str) -> bool:
    normalized = _norm(text)
    return _contains_any(
        normalized,
        [
            "what should i measure for",
            "what to measure for",
            "what files do i need for",
            "which files do i need for",
            "what rfi should i ask",
            "what rfis should i ask",
            "what rfi should i raise",
            "what rfis should i raise",
        ],
    )


def _future_tool_requested(matches: list[dict[str, Any]], text: str) -> bool:
    normalized = _norm(text)
    future_tools = {
        "future_tool_advisor",
        "formatter",
        "qa_checker",
        "client_document_reader",
        "omission_addition",
        "compare_boq",
    }
    if _contains_any(
        normalized,
        [
            "which tool",
            "which capability",
            "future tool",
            "available tool",
            "run o&a",
            "run omission",
            "run qa",
            "run formatter",
            "run document reader",
            "compare old and revised boq",
            "old and revised boq",
        ],
    ):
        return True
    for match in matches:
        if str(match.get("capability")) in {"future_tool_advisory", "workbook_tool_ambiguity"}:
            return True
        if future_tools.intersection(set(match.get("tool_candidates") or [])):
            return True
    return False


def _future_tool_execution_requested(text: str) -> bool:
    normalized = _norm(text)
    return _contains_any(
        normalized,
        [
            "run o&a",
            "run omission",
            "run qa",
            "run formatter",
            "run document reader",
            "execute o&a",
            "execute qa",
            "execute formatter",
            "start o&a",
            "start qa checker",
            "process this report",
            "compare old and revised boq",
        ],
    )


def _clarification_questions_for_unknown_scope() -> list[str]:
    return [
        "Which trade/package is this under?",
        "Which measurement standard or client format should I use?",
        "Do you have drawings, specification, schedules, or consultant reports?",
    ]


def requirement_check(request_text: str) -> dict[str, Any]:
    """Deterministic metadata-only requirement advisor.

    This never calls models, tools, installers, connectors, workbook readers, or
    Builder execution paths. It only maps user text to registry capabilities.
    """
    text = _norm(request_text)
    safety = registry_safety_payload()
    matches: list[dict[str, Any]] = []

    def add(capability: str, status: str, reason: str, *, tools: list[str] | None = None, connectors: list[str] | None = None, required_files: list[str] | None = None, requirements: list[str] | None = None, outputs: list[str] | None = None, risk: str = "medium") -> None:
        matches.append({
            "capability": capability,
            "status": status,
            "reason": reason,
            "tool_candidates": tools or [],
            "connector_candidates": connectors or [],
            "required_files": required_files or [],
            "requirements": requirements or [],
            "outputs": outputs or [],
            "risk_level": risk,
            "execution_enabled": False,
            "metadata_only": True,
        })

    if _contains_any(text, [
        "enable cell read",
        "formula read",
        "enable workbook read",
        "workbook read",
        "read cells",
        "read formulas",
        "open workbook",
        "parse workbook",
        "workbook cells",
        "workbook data",
        "extract all workbook data",
        "openpyxl",
        "bypass workbook policy",
        "expose workbook folder",
        "unlock workbook read gate",
        "future_formula_token",
        "future formula token",
        "workbook reader",
        "execute it",
        "builder engine",
        "legacy builder",
        "create excel",
    ]):
        add(
            "workbook_read_or_engine_execution_policy",
            "blocked_metadata_only_requires_fire_policy",
            "registry_cannot_enable_workbook_read_or_engine",
            tools=["builder"],
            requirements=["explicit_future_policy", "FIRE_approval", "workbook_read_boundary"],
            outputs=["policy_warning"],
            risk="high",
        )

    if _contains_any(text, ["what should i measure", "what to measure", "measurement checklist", "assigned to", "scope checklist", "boq checklist", "report checklist", "scope from report"]):
        trade = _matched_scope_item(text)
        add(
            "qs_scope_advice",
            "available_metadata_only",
            f"scope_advisor:{(trade or {}).get('scope_advisor_key', 'general_trade_scope')}",
            tools=["qs_scope_advisor"],
            required_files=(trade or {}).get("files_required") or ["drawings", "specification"],
            outputs=(trade or {}).get("outputs") or ["measurement_checklist", "rfi_drafts", "scope_risk_register"],
            risk=(trade or {}).get("risk_level", "medium"),
        )

    if _contains_any(text, ["rfi", "request for information", "clarification", "raise a question"]):
        add(
            "draft_rfi",
            "available_metadata_only",
            "rfi_generator_metadata_only",
            tools=["rfi_generator"],
            required_files=["drawings", "specification", "scope_gap_or_question"],
            outputs=["rfi_draft", "clarification_register_item"],
            risk="low_medium",
        )

    if _contains_any(text, ["scanned", "ocr", "read this report", "acoustic report", "fire report", "fire engineering report", "access report", "j1v3", "jv3", "consultant report", "pdf report", "boq checklist from", "checklist from fire report", "checklist from consultant report"]):
        add(
            "document_ocr_or_report_reader",
            "planned_requires_install_or_model",
            "document_reader_ocr_requirement",
            tools=["client_document_reader"],
            requirements=["pymupdf_or_pypdf", "ocrmypdf_or_tesseract_for_scanned_pdf", "vision_model_optional"],
            outputs=["read_only_summary", "qs_scope_checklist", "scope_risk_register"],
            risk="medium",
        )

    if _contains_any(text, ["control my lights", "smart home", "home assistant", "alexa", "siri", "google home", "apple home", "matter bridge", "matter device", "turn on lights"]):
        add(
            "smart_home_control",
            "future_connector_required",
            "ecosystem_adapter_required",
            connectors=["home_assistant", "matter_bridge", "apple_home", "google_home_android", "alexa_skill"],
            requirements=["auth_token", "entity_allowlist", "command_safety_policy", "user_confirmation_for_risky_devices"],
            outputs=["device_state_read", "approved_scene_trigger_future"],
            risk="high",
        )

    if _contains_any(text, ["android", "ios", "iphone", "ipad", "mobile app", "apple app"]):
        add(
            "mobile_client",
            "planned_metadata_only",
            "mobile_app_client_future",
            connectors=["mobile_android", "mobile_ios"],
            requirements=["api_auth", "device_session_policy", "offline_cache_policy"],
            outputs=["mobile_client_shell_future"],
            risk="medium_high",
        )

    if _contains_any(text, ["cloudflare", "remote access", "public url", "tunnel", "outside my network"]):
        add(
            "remote_access_connector",
            "planned_high_risk_connector_required",
            "cloudflare_tunnel_metadata_only",
            connectors=["cloudflare_tunnel", "cloudflare_access"],
            requirements=["access_policy", "auth_gate", "no_direct_public_workbook_folder", "local_firewall_rules"],
            outputs=["remote_access_plan"],
            risk="high",
        )

    if _contains_any(text, ["patch jarvis", "codex", "github", "coding", "write code", "fix code", "router patch"]):
        add(
            "code_patch_worker",
            "planned_requires_fire_and_repo_policy",
            "codex_github_connector_required",
            tools=["codex_github"],
            requirements=["git_repo_connected", "AGENTS.md", "protected_system_rules", "test_command_defined", "FIRE_approval"],
            outputs=["scoped_patch_plan", "diff_review", "test_report"],
            risk="high",
        )

    if _contains_any(text, ["check this workbook", "audit workbook", "compare workbook", "compare boq", "omission", "addition", "o&a", "format workbook", "qa check"]):
        add(
            "workbook_tool_ambiguity",
            "requires_clarification_no_execution",
            "multiple_workbook_capabilities_possible",
            tools=["formatter", "qa_checker", "omission_addition", "compare_boq", "builder"],
            required_files=["workbook"],
            outputs=["tool_choice_clarification"],
            risk="medium",
        )

    if _contains_any(text, ["what files do i need", "which files do i need", "required files", "file requirement", "file checklist", "drawings do i need", "documents do i need"]):
        trade = _matched_scope_item(text)
        add(
            "file_requirement_advice",
            "available_metadata_only",
            f"file_requirement_advisor:{(trade or {}).get('scope_advisor_key', 'general_scope')}",
            tools=["file_requirement_advisor", "qs_scope_advisor"],
            required_files=(trade or {}).get("files_required") or ["drawings", "specification", "schedules"],
            outputs=["required_files", "optional_files", "missing_information_questions"],
            risk=(trade or {}).get("risk_level", "low"),
        )

    if _contains_any(text, ["scope risk", "risk checklist", "scope-risk", "missing scope", "boq items may be missing", "scope gap", "scope impacts", "scope risks"]):
        add(
            "scope_risk_checklist",
            "available_metadata_only",
            "scope_risk_checklist_metadata_only",
            tools=["qs_scope_advisor", "rfi_generator"],
            required_files=["drawings", "specification", "relevant_consultant_report_or_schedule"],
            outputs=["scope_risk_register", "review_checklist", "rfi_templates"],
            risk="low_medium",
        )

    if _contains_any(text, ["which tool", "which capability", "what tool should", "tool should handle", "capability should handle", "future tool", "available tool", "can jarvis do", "run o&a", "run omission", "run qa", "run formatter", "run document reader", "execute o&a", "execute qa", "execute formatter", "process this report", "compare old and revised boq", "old and revised boq"]):
        add(
            "future_tool_advisory",
            "metadata_only_no_execution",
            "future_tool_capability_advisory",
            tools=["future_tool_advisor"],
            outputs=["tool_choice_guidance", "capability_requirements", "safe_next_actions"],
            risk="low",
        )

    if _contains_any(text, ["standard", "ncc", "bca", "eurocode", "nrm", "anzsmm", "cesmm", "icsm", "icms", "council standard", "as/nzs"]):
        add(
            "standards_reference_lookup",
            "metadata_reference_only",
            "standards_kb_not_connected",
            tools=["standards_knowledge_base"],
            requirements=["jurisdiction", "source_version", "project_context", "source_upload_for_clause_advice"],
            outputs=["reference_checklist", "source_authority_warning"],
            risk="medium_high",
        )

    if not matches:
        add(
            "general_capability_triage",
            "metadata_only_no_specific_match",
            "no_deterministic_requirement_match",
            tools=[],
            outputs=["ask_clarifying_question"],
            risk="low",
        )

    risk_level = _highest_risk(matches)
    requires_approval = _requires_registry_approval(matches)
    scope_item = _matched_scope_item(text)
    scope_advisory_requested = _scope_advisory_requested(text)
    known_scope = bool(scope_item) if scope_advisory_requested else None
    unknown_scope = bool(scope_advisory_requested and not scope_item)
    future_tool_requested = _future_tool_requested(matches, text)
    execution_requested = _future_tool_execution_requested(text)
    execution_blocked = bool(future_tool_requested and execution_requested)
    requires_clarification = (
        len(matches) > 1
        or (matches and str(matches[0]["status"]).startswith("requires"))
        or unknown_scope
        or execution_blocked
    )
    return {
        "route": "registry_requirement_check",
        "request": request_text,
        "matches": matches,
        "top_match": matches[0] if matches else None,
        "capability_candidates": [m["capability"] for m in matches],
        "tool_candidates": sorted({tool for m in matches for tool in m.get("tool_candidates", [])}),
        "connector_candidates": sorted({connector for m in matches for connector in m.get("connector_candidates", [])}),
        "requires_clarification": requires_clarification,
        "risk_level": risk_level,
        "requires_approval": requires_approval,
        "advisory_type": _advisory_type_for_matches(matches, request_text),
        "advisory_route": _advisory_type_for_matches(matches, request_text),
        "builder_mutation_allowed": False,
        "active_task_mutated": False,
        "requires_file_read": False,
        "future_tool_requested": future_tool_requested,
        "execution_requested": execution_requested,
        "execution_blocked": execution_blocked,
        "blocked_reason": "future_tool_execution_disabled" if execution_blocked else None,
        "known_scope": known_scope,
        "unknown_scope": unknown_scope,
        "clarification_questions": _clarification_questions_for_unknown_scope() if unknown_scope else [],
        "all_entries_execution_disabled": True,
        **safety,
    }


def route_capability_diagnostics(text: str) -> dict[str, Any] | None:
    result = requirement_check(text)
    top = result.get("top_match") or {}
    if top.get("capability") == "general_capability_triage":
        return None
    return {
        "capability": top.get("capability"),
        "status": top.get("status"),
        "reason": top.get("reason"),
        "capability_candidates": result.get("capability_candidates", []),
        "tool_candidates": result.get("tool_candidates", []),
        "connector_candidates": result.get("connector_candidates", []),
        "execution_enabled": False,
        "metadata_only": True,
    }
