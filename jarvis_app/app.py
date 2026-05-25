from __future__ import annotations

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
import uuid
from jarvis_app.config import APP_NAME, APP_VERSION
from jarvis_app.core.state_kernel import StateKernel
from jarvis_app.router.main_router import MainRouter, public_workbook_ref
from jarvis_app.schemas.message_schema import AttachmentMeta, ChatRequest, ChatResponse, DebugClarificationRequest, DebugClarificationResponse, SnapshotCreateRequest, SnapshotCreateResponse, BuilderAdapterDryRunRequest, BuilderAdapterDryRunResponse, BuilderEngineContractRequest, BuilderEngineContractResponse, BuilderEngineBoundaryAuditRequest, BuilderEngineBoundaryAuditResponse, BuilderEnginePreflightRequest, BuilderEnginePreflightResponse, BuilderEngineExecutionRequest, BuilderEngineExecutionResponse, LegacyBridgeShadowProbeRequest, LegacyBridgeShadowProbeResponse, PreviewExecutionPolicyRequest, PreviewExecutionPolicyResponse, SafeWorkbookPathResolverDryRunRequest, SafeWorkbookPathResolverDryRunResponse, WorkbookReadPreflightDryRunRequest, WorkbookReadPreflightDryRunResponse, WorkbookMetadataProbeApprovalRequest, WorkbookMetadataProbeApprovalResponse, WorkbookSheetNameProbeApprovalRequest, WorkbookSheetNameProbeApprovalResponse, WorkbookReadPolicyReviewRequest, WorkbookReadPolicyReviewResponse
from jarvis_app.schemas.builder_plan_schema import plan_summary
from jarvis_app.schemas.builder_snapshot_schema import build_snapshot_from_active_task, plan_hash_from_plan
from jarvis_app.tools.builder.adapter_dry_run import run_builder_adapter_dry_run, adapter_trace_payload
from jarvis_app.tools.builder.engine_contract_adapter import create_builder_engine_contract, contract_trace_payload
from jarvis_app.tools.builder.engine_boundary_audit import audit_builder_engine_boundary, boundary_audit_summary
from jarvis_app.tools.builder.engine_preflight import run_engine_preflight, preflight_summary
from jarvis_app.tools.builder.setup_completeness import setup_completeness_from_plan, setup_completeness_from_snapshot
from jarvis_app.tools.builder.legacy_engine_bridge import prepare_legacy_builder_execution_request, execution_summary, execution_lock_status
from jarvis_app.tools.builder.contract_fixture_replay import run_contract_fixture_replay
from jarvis_app.tools.builder.legacy_import_boundary_audit import run_legacy_import_boundary_audit, latest_legacy_import_boundary_audit, latest_legacy_import_boundary_audit_summary
from jarvis_app.tools.builder.legacy_bridge_shadow_probe import run_legacy_bridge_shadow_probe
from jarvis_app.tools.builder.preview_execution_policy import evaluate_preview_execution_policy
from jarvis_app.tools.builder.safe_workbook_path_resolver import evaluate_safe_workbook_path_resolver_dry_run
from jarvis_app.tools.builder.workbook_read_preflight_contract import evaluate_workbook_read_preflight_dry_run
from jarvis_app.tools.builder.workbook_metadata_probe_approval import evaluate_workbook_metadata_probe_approval
from jarvis_app.tools.builder.workbook_sheet_name_probe_approval import evaluate_workbook_sheet_name_probe_approval
from jarvis_app.tools.builder.workbook_read_policy_review import evaluate_workbook_read_policy_review
from jarvis_app.parsers.conflict_guard import plan_normalization_report
from jarvis_app.core.readiness_contract import build_readiness_contract
from jarvis_app.qa_runner.test_executor import TestPackExecutor, validate_loaded_pack
from jarvis_app.qa_runner.test_pack_loader import TestPackLoadError, load_test_pack
from jarvis_app.registry.registry_loader import list_registry, requirement_check, registry_safety_payload
from jarvis_app.schemas.registry_schema import RegistryRequirementCheckRequest, RegistryRequirementCheckResponse

app = FastAPI(title=APP_NAME, version=APP_VERSION)
kernel = StateKernel()
router = MainRouter(kernel)


def no_engine_safety_payload() -> dict:
    """Canonical no-engine safety envelope for Builder API responses."""
    return {
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
    }


def with_no_engine_safety(payload: dict) -> dict:
    """Add consistent top-level and nested no-engine safety fields.

    This is intentionally additive and does not mutate Builder plans, snapshots,
    adapters, contracts, or execution logic.
    """
    safety = no_engine_safety_payload()
    for key, value in safety.items():
        payload.setdefault(key, value)
    nested = dict(safety)
    nested.update(payload.get("safety") or {})
    for key, value in safety.items():
        nested[key] = bool(nested.get(key, value))
    payload["safety"] = nested
    return payload


def no_active_task_plan_payload(conversation_id: str, reason: str) -> dict:
    """Consistent safe /api/plan payload when no active Builder task exists.

    This does not create or imply a Builder task. It only exposes the no-engine
    safety envelope so imported packs and callers can verify safety without
    relying on endpoint-specific paths.
    """
    safety = no_engine_safety_payload()
    empty_snapshot = {"found": False}
    empty_adapter = {"found": False}
    empty_contract = {"found": False}
    workbook_read_policy = _latest_workbook_read_policy_review_for_conversation(conversation_id)
    return {
        "found": False,
        "version": APP_VERSION,
        "conversation_id": conversation_id,
        "reason": reason,
        "safety": dict(safety),
        "latest_snapshot": empty_snapshot,
        "latest_adapter": empty_adapter,
        "latest_engine_contract": empty_contract,
        "snapshot": empty_snapshot,
        "adapter_dry_run": empty_adapter,
        "engine_contract": empty_contract,
        "active_task": {
            "found": False,
            "task_id": None,
            "tool": None,
            "status": None,
            "workbook_found": False,
            "pending_clarification": False,
        },
        "plan_summary": {},
        "workbook_read_policy": workbook_read_policy,
        "readiness": {
            "status": "no_active_task",
            "workbook_read_policy_status": workbook_read_policy.get("status") or "not_reviewed",
            "workbook_read_policy_reviewed": workbook_read_policy.get("status") == "reviewed",
            "workbook_read_policy": {
                "found": bool(workbook_read_policy.get("found")),
                "status": workbook_read_policy.get("status") or "not_reviewed",
                "policy_only": True,
                "workbook_opened": False,
                "workbook_read": False,
                "workbook_content_read": False,
                "cells_read": False,
                "formulas_read": False,
                "engine_called": False,
                "excel_created": False,
                "legacy_builder_called": False,
            },
            "safety": dict(safety),
        },
        "legacy_import_boundary_audit": latest_legacy_import_boundary_audit_summary(conversation_id),
    }


def _log_debug_trace(conversation_id: str, req_obj, response_payload: dict) -> None:
    """Record debug-only endpoint actions in the same router trace ledger.

    This keeps Swagger/manual debug actions visible beside /api/chat events
    without connecting any Builder, Formatter, QA, or slot-reducer logic.
    """
    if not conversation_id:
        return
    kernel.events.append(
        conversation_id,
        client_event_id=getattr(req_obj, "client_event_id", None),
        intent=response_payload.get("intent", "DEBUG"),
        route=response_payload.get("route", "debug"),
        request=req_obj.model_dump(mode="json"),
        response=response_payload,
    )


@app.get("/api/version")
def api_version() -> dict:
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "scope": "workbook_read_policy_review_no_content_read",
        "engines_connected": {
            "builder": False,
            "formatter": False,
            "qa_checker": False,
            "omission_addition": False,
            "builder_engine_contract": False,
            "builder_engine_contract_replay": False,
            "builder_engine_preflight": False,
            "builder_engine_execution": False,
            "builder_contract_fixture_replay": False,
            "legacy_import_boundary_audit": False,
            "legacy_bridge_shadow_probe": False,
            "preview_execution_policy": False,
            "safe_workbook_path_resolver_dry_run": False,
            "workbook_read_preflight_contract": False,
            "workbook_metadata_probe_approval": False,
            "workbook_sheet_name_probe_approval": False,
            "workbook_read_policy_review": False,
            "local_qa_runner": False,
            "test_pack_import_guard": False,
        },
        "execution_locks": execution_lock_status(),
        "scope_metadata": {
            "minimal_pair_route_ownership_hygiene": True,
            "no_active_action_needs_active_task": True,
            "weakness_replay_compatibility_cleanup": True,
            "active_action_diagnostic_alias": True,
            "version_lock_policy_documented": True,
            "parser_signal_helper_owner": True,
            "formworks_unit_compatibility_guard": True,
            "pending_clarification_risky_action_coverage": True,
            "pending_clarification_run_builder_block": True,
            "active_task_non_mutating_language_gate": True,
            "active_task_wrapper_in_plan": True,
            "central_unit_aliases": {
                "sqm": "m2",
                "sq m": "m2",
                "sq.m": "m2",
                "sq. m": "m2",
                "sq metres": "m2",
                "sq meters": "m2",
                "square metres": "m2",
                "square meters": "m2",
                "m²": "m2"
            },
            "engineering_language_gate": True,
            "engineering_choose_tool_ambiguity": True,
            "active_task_action_language_gate": True,
            "registry_advisory_metadata_only_route": True,
            "route_decision_single_source_context": True,
            "active_task_context_unhandled_route": True,
            "global_capability_registry": True,
            "qs_scope_advisor_registry": True,
            "rfi_template_registry": True,
            "ecosystem_adapter_map": True,
            "requirement_advisor": True,
            "registry_endpoints_metadata_only": True,
            "future_tools_execution_enabled": False,
            "legacy_bridge_shadow_probe": True,
            "workbook_access_boundary_policy": True,
            "preview_execution_policy_metadata_only": True,
            "policy_response_hygiene": True,
            "contract_summary_public_only": True,
            "approval_token_policy_schema_defined": True,
            "preview_approval_readiness_defined": True,
            "export_approval_readiness_defined": True,
            "preview_result_schema_defined": True,
            "output_manifest_schema_defined": True,
            "background_job_boundary_policy": True,
            "formula_integrity_guard_connection_point_defined": True,
            "safe_workbook_path_resolver_dry_run": True,
            "workbook_path_resolution_enabled": False,
            "workbook_filesystem_check_enabled": False,
            "workbook_open_enabled": False,
            "workbook_read_preflight_contract": True,
            "workbook_read_preflight_metadata_only": True,
            "workbook_metadata_probe_approval_contract": True,
            "workbook_metadata_probe_approval_required_by_default": True,
            "workbook_metadata_probe_metadata_only": True,
            "workbook_sheet_name_probe_approval_contract": True,
            "workbook_sheet_name_probe_approval_required_by_default": True,
            "workbook_sheet_names_enabled": True,
            "workbook_parse_enabled": False,
            "workbook_read_policy_review_contract": True,
            "cell_read_enabled": False,
            "formula_read_enabled": False,
            "dimension_read_enabled": False,
            "no_workbook_read": True,
            "no_engine": True,
        },
    }


def _registry_response(registry_name: str) -> dict:
    payload = list_registry(registry_name)
    payload.update(registry_safety_payload())
    route_name = f"registry_{registry_name}"
    if registry_name == "execution_policies":
        route_name = "registry_execution_policies"
    payload.setdefault("route", route_name)
    return payload


@app.get("/api/registry/tools")
def api_registry_tools() -> dict:
    return _registry_response("tools")


@app.get("/api/registry/capabilities")
def api_registry_capabilities() -> dict:
    return _registry_response("capabilities")


@app.get("/api/registry/connectors")
def api_registry_connectors() -> dict:
    return _registry_response("connectors")


@app.get("/api/registry/models")
def api_registry_models() -> dict:
    return _registry_response("models")


@app.get("/api/registry/execution-policies")
def api_registry_execution_policies() -> dict:
    return _registry_response("execution_policies")


@app.get("/api/registry/source-authorities")
def api_registry_source_authorities() -> dict:
    return _registry_response("source_authorities")


@app.get("/api/registry/scope-advisors")
def api_registry_scope_advisors() -> dict:
    return _registry_response("scope_advisors")


@app.get("/api/registry/file-requirements")
def api_registry_file_requirements() -> dict:
    return _registry_response("file_requirements")


@app.get("/api/registry/rfi-templates")
def api_registry_rfi_templates() -> dict:
    return _registry_response("rfi_templates")


@app.get("/api/registry/ecosystem-adapters")
def api_registry_ecosystem_adapters() -> dict:
    return _registry_response("ecosystem_adapters")


@app.get("/api/registry/voice-assistants")
def api_registry_voice_assistants() -> dict:
    return _registry_response("voice_assistants")


@app.post("/api/registry/requirement-check", response_model=RegistryRequirementCheckResponse)
def api_registry_requirement_check(req: RegistryRequirementCheckRequest) -> RegistryRequirementCheckResponse:
    return RegistryRequirementCheckResponse.model_validate(requirement_check(req.request))


def _apply_chat_response_shape_compatibility(response: dict) -> dict:
    """Add compatibility-only chat response fields without changing routing.

    plan_mutated is a public response-shape alias needed by external packs.
    True mutation signals must win over the default False value.
    """
    if isinstance(response.get("plan_mutated"), bool):
        return response
    reducer_result = response.get("reducer_result")
    if isinstance(reducer_result, dict):
        reducer_plan_mutated = reducer_result.get("plan_mutated")
        if isinstance(reducer_plan_mutated, bool):
            response["plan_mutated"] = reducer_plan_mutated
            return response
        changed_slots = reducer_result.get("changed_slots")
        if isinstance(changed_slots, list) and bool(changed_slots):
            response["plan_mutated"] = True
            return response
    response["plan_mutated"] = False
    return response


@app.post("/api/chat")
def api_chat(req: ChatRequest) -> dict:
    response = router.route(req).model_dump(mode="json")
    response = _apply_chat_response_shape_compatibility(response)
    if response.get("route") == "active_task_non_mutating_language" and response.get("reducer_result") is None:
        response.pop("reducer_result", None)
    for optional_key in ("registry_assist", "requirement_advisor", "non_mutating_category", "active_task_action_language", "metadata_only", "execution_enabled", "workbook_read", "engine_called", "excel_created", "legacy_builder_called", "safety"):
        if response.get(optional_key) is None:
            response.pop(optional_key, None)
    if not response.get("capability_candidates"):
        response.pop("capability_candidates", None)
    return response


@app.post("/api/attach", response_model=ChatResponse)
def api_attach(
    conversation_id: str | None = Form(default=None),
    client_event_id: str | None = Form(default=None),
    text: str = Form(default="Here"),
    file: UploadFile = File(...),
) -> ChatResponse:
    try:
        saved = kernel.attachments.save_upload(file)
    except Exception as exc:
        state = kernel.conversations.get_or_create(conversation_id)
        task = kernel.tasks.get(state.active_task_id) if state.active_task_id else None
        payload = {
            "conversation_id": state.conversation_id,
            "event_id": f"evt_{uuid.uuid4().hex}",
            "intent": "ATTACHMENT_ONLY",
            "route": "attachment_save_failed",
            "message": "Workbook upload failed before binding. No task state was changed.",
            "active_task_id": task.task_id if task else None,
            "active_task_status": task.status if task else None,
            "pending_clarification_id": state.pending_clarification_id,
            "blocked": True,
            "reason": "attachment_save_failed",
            "router_step": "attachment_save",
            "duplicate": False,
            "state": state.model_dump(mode="json"),
            "reducer_result": {
                "error": type(exc).__name__,
                "detail": str(exc),
                "workbook_read": False,
            },
            "snapshot": None,
            "adapter": None,
            "setup_completeness": None,
        }
        kernel.events.append(
            state.conversation_id,
            client_event_id=client_event_id,
            intent=payload["intent"],
            route=payload["route"],
            request={
                "conversation_id": conversation_id,
                "text": text,
                "client_event_id": client_event_id,
                "attachments": [{"filename": file.filename, "content_type": file.content_type}],
            },
            response=payload,
        )
        return ChatResponse.model_validate(payload)

    req = ChatRequest(
        conversation_id=conversation_id,
        client_event_id=client_event_id,
        text=text,
        attachments=[AttachmentMeta(**saved)],
    )
    return router.route(req)


@app.post("/api/debug/create-test-clarification", response_model=DebugClarificationResponse)
def api_debug_create_test_clarification(req: DebugClarificationRequest) -> DebugClarificationResponse:
    state = kernel.conversations.get(req.conversation_id)
    if not state:
        payload = {
            "conversation_id": req.conversation_id,
            "active_task_id": None,
            "pending_clarification_id": None,
            "route": "debug_create_test_clarification",
            "message": "No conversation found for this id.",
            "status": None,
            "blocked": True,
            "reason": "conversation_not_found",
            "router_step": "debug_create_test_clarification",
            "intent": "DEBUG",
            "state": {},
        }
        _log_debug_trace(req.conversation_id, req, payload)
        return DebugClarificationResponse.model_validate(with_no_engine_safety(payload))
    task = kernel.tasks.get(state.active_task_id)
    if not task:
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": None,
            "pending_clarification_id": None,
            "route": "debug_create_test_clarification",
            "message": "No active task exists. Create a Builder shell task first.",
            "status": None,
            "blocked": True,
            "reason": "no_active_task",
            "router_step": "debug_create_test_clarification",
            "intent": "DEBUG",
            "state": state.model_dump(mode="json"),
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return DebugClarificationResponse.model_validate(with_no_engine_safety(payload))

    import uuid
    from datetime import datetime, timezone

    clarification = {
        "clarification_id": f"clar_{uuid.uuid4().hex}",
        "task_id": task.task_id,
        "type": "test_choice",
        "prompt": req.prompt or "Choose A or B.",
        "options": req.options or ["A", "B", "Cancel"],
        "expected_answer_classes": ["a", "b", "cancel"],
        "resolver_name": "resolve_test_choice",
        "context": {"debug_only": True},
        "repeats": 0,
        "max_repeats": 2,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    task.pending_clarification = clarification
    task.status = "needs_clarification"
    state.pending_clarification_id = clarification["clarification_id"]
    kernel.tasks.save(task)
    kernel.conversations.save(state)

    payload = {
        "conversation_id": state.conversation_id,
        "active_task_id": task.task_id,
        "pending_clarification_id": clarification["clarification_id"],
        "route": "debug_create_test_clarification",
        "message": "Test clarification created. DEBUG ONLY — no Builder logic was executed.",
        "status": "open",
        "blocked": False,
        "reason": "debug_test_clarification_created",
        "router_step": "debug_create_test_clarification",
        "intent": "DEBUG",
        "state": state.model_dump(mode="json"),
    }
    _log_debug_trace(state.conversation_id, req, payload)
    return DebugClarificationResponse.model_validate(with_no_engine_safety(payload))


@app.post("/api/builder/create-snapshot", response_model=SnapshotCreateResponse)
def api_builder_create_snapshot(req: SnapshotCreateRequest) -> SnapshotCreateResponse:
    state = kernel.conversations.get(req.conversation_id)
    if not state:
        payload = {
            "conversation_id": req.conversation_id,
            "active_task_id": None,
            "snapshot_id": None,
            "route": "builder_snapshot_blocked",
            "message": "No conversation found for this id.",
            "valid": False,
            "blocked": True,
            "reason": "conversation_not_found",
            "router_step": "builder_snapshot_create",
            "snapshot_hash": None,
            "validation": {"valid": False, "issues": ["Conversation not found"], "warnings": []},
            "state": {},
            "snapshot": None,
            "intent": "BUILDER_SNAPSHOT",
        }
        _log_debug_trace(req.conversation_id, req, payload)
        return SnapshotCreateResponse.model_validate(with_no_engine_safety(payload))

    task = kernel.tasks.get(state.active_task_id)
    if not task:
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": None,
            "snapshot_id": None,
            "route": "builder_snapshot_blocked",
            "message": "No active Builder task exists. Create a Builder shell task first.",
            "valid": False,
            "blocked": True,
            "reason": "no_active_task",
            "router_step": "builder_snapshot_create",
            "snapshot_hash": None,
            "validation": {"valid": False, "issues": ["No active task"], "warnings": []},
            "state": state.model_dump(mode="json"),
            "snapshot": None,
            "intent": "BUILDER_SNAPSHOT",
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return SnapshotCreateResponse.model_validate(with_no_engine_safety(payload))

    if task.tool != "builder":
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": task.task_id,
            "snapshot_id": None,
            "route": "builder_snapshot_blocked",
            "message": "The active task is not a Builder task.",
            "valid": False,
            "blocked": True,
            "reason": "active_task_not_builder",
            "router_step": "builder_snapshot_create",
            "snapshot_hash": None,
            "validation": {"valid": False, "issues": ["Active task is not builder"], "warnings": []},
            "state": state.model_dump(mode="json"),
            "snapshot": None,
            "intent": "BUILDER_SNAPSHOT",
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return SnapshotCreateResponse.model_validate(with_no_engine_safety(payload))

    if task.pending_clarification or state.pending_clarification_id:
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": task.task_id,
            "snapshot_id": None,
            "route": "builder_snapshot_blocked",
            "message": "Snapshot blocked because a clarification is still open. Resolve or cancel it first.",
            "valid": False,
            "blocked": True,
            "reason": "pending_clarification_blocks_snapshot",
            "router_step": "builder_snapshot_create",
            "snapshot_hash": None,
            "validation": {"valid": False, "issues": ["Pending clarification exists"], "warnings": []},
            "state": state.model_dump(mode="json"),
            "snapshot": None,
            "intent": "BUILDER_SNAPSHOT",
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return SnapshotCreateResponse.model_validate(with_no_engine_safety(payload))

    snapshot = build_snapshot_from_active_task(
        snapshot_id=kernel.snapshots.new_id(),
        conversation_id=state.conversation_id,
        task=task,
        approve=req.approve,
    )
    if not snapshot.validation.valid:
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": task.task_id,
            "snapshot_id": None,
            "route": "builder_snapshot_blocked",
            "message": "Snapshot blocked because active Builder state is structurally invalid.",
            "valid": False,
            "blocked": True,
            "reason": "snapshot_validation_failed",
            "router_step": "builder_snapshot_create",
            "snapshot_hash": None,
            "validation": snapshot.validation.model_dump(mode="json"),
            "state": state.model_dump(mode="json"),
            "snapshot": snapshot.model_dump(mode="json"),
            "intent": "BUILDER_SNAPSHOT",
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return SnapshotCreateResponse.model_validate(with_no_engine_safety(payload))

    kernel.snapshots.save(snapshot)
    payload = {
        "conversation_id": state.conversation_id,
        "active_task_id": task.task_id,
        "snapshot_id": snapshot.snapshot_id,
        "route": "builder_snapshot_created",
        "message": f"Builder snapshot created from the active plan. Preview/export engines are still not connected in {APP_VERSION}.",
        "valid": snapshot.validation.valid,
        "blocked": False,
        "reason": "builder_snapshot_created_from_active_task",
        "router_step": "builder_snapshot_create",
        "snapshot_hash": snapshot.snapshot_hash,
        "snapshot_status": snapshot.status,
        "stale_reason": snapshot.stale_reason,
        "source_plan_hash": snapshot.source_plan_hash,
        "active_plan_hash": snapshot.active_plan_hash,
        "validation": snapshot.validation.model_dump(mode="json"),
        "state": state.model_dump(mode="json"),
        "snapshot": snapshot.model_dump(mode="json"),
        "setup_completeness": snapshot.setup_completeness,
        "readiness": _readiness_payload_for_conversation(state.conversation_id),
        "intent": "BUILDER_SNAPSHOT",
    }
    _log_debug_trace(state.conversation_id, req, payload)
    return SnapshotCreateResponse.model_validate(with_no_engine_safety(payload))


@app.get("/api/builder/snapshot/{snapshot_id}")
def api_builder_snapshot(snapshot_id: str) -> dict:
    snapshot = kernel.snapshots.get(snapshot_id)
    if not snapshot:
        return {"found": False, "snapshot_id": snapshot_id, "reason": "snapshot_not_found"}
    return {"found": True, "snapshot": snapshot.model_dump(mode="json")}


@app.get("/api/builder/active-snapshot/{conversation_id}")
def api_builder_active_snapshot(conversation_id: str) -> dict:
    snapshot = kernel.snapshots.get_active(conversation_id)
    if not snapshot:
        return {"found": False, "conversation_id": conversation_id, "reason": "active_snapshot_not_found"}
    snapshot_ctx = _snapshot_context_for_conversation(conversation_id) or {}
    snapshot_payload = snapshot.model_dump(mode="json")
    snapshot_payload.update({
        "status": snapshot_ctx.get("status", snapshot.status),
        "stale_reason": snapshot_ctx.get("stale_reason", snapshot.stale_reason),
        "active_plan_hash": snapshot_ctx.get("active_plan_hash", snapshot.active_plan_hash),
    })
    snapshot_payload["setup_completeness"] = setup_completeness_from_snapshot(snapshot_payload)
    return {
        "found": True,
        "conversation_id": conversation_id,
        "snapshot_status": snapshot_payload.get("status"),
        "stale_reason": snapshot_payload.get("stale_reason"),
        "active_plan_hash": snapshot_payload.get("active_plan_hash"),
        "snapshot": snapshot_payload,
    }


@app.post("/api/builder/adapter-dry-run", response_model=BuilderAdapterDryRunResponse)
def api_builder_adapter_dry_run(req: BuilderAdapterDryRunRequest) -> BuilderAdapterDryRunResponse:
    state = kernel.conversations.get(req.conversation_id)
    if not state:
        payload = {
            "conversation_id": req.conversation_id,
            "active_task_id": None,
            "snapshot_id": req.snapshot_id,
            "adapter_input_id": None,
            "route": "builder_adapter_dry_run_blocked",
            "message": "Builder adapter dry run blocked because the conversation was not found.",
            "blocked": True,
            "reason": "conversation_not_found",
            "router_step": "builder_adapter_dry_run",
            "adapter_status": "blocked",
            "engine_called": False,
            "excel_created": False,
            "workbook_read": False,
            "adapter_input": None,
            "validation": {"valid_for_dry_run": False, "valid_for_future_engine": False, "issues": ["Conversation not found"], "warnings": []},
            "state": {},
            "snapshot": None,
            "adapter": None,
            "intent": "BUILDER_ADAPTER_DRY_RUN",
        }
        _log_debug_trace(req.conversation_id, req, payload)
        return BuilderAdapterDryRunResponse.model_validate(with_no_engine_safety(payload))

    task = kernel.tasks.get(state.active_task_id)
    if not task or task.tool != "builder":
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": task.task_id if task else None,
            "snapshot_id": req.snapshot_id,
            "adapter_input_id": None,
            "route": "builder_adapter_dry_run_blocked",
            "message": "Builder adapter dry run blocked because there is no active Builder task.",
            "blocked": True,
            "reason": "no_active_builder_task",
            "router_step": "builder_adapter_dry_run",
            "adapter_status": "blocked",
            "engine_called": False,
            "excel_created": False,
            "workbook_read": False,
            "adapter_input": None,
            "validation": {"valid_for_dry_run": False, "valid_for_future_engine": False, "issues": ["No active Builder task"], "warnings": []},
            "state": state.model_dump(mode="json"),
            "snapshot": None,
            "adapter": None,
            "intent": "BUILDER_ADAPTER_DRY_RUN",
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderAdapterDryRunResponse.model_validate(with_no_engine_safety(payload))

    if task.pending_clarification or state.pending_clarification_id:
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": task.task_id,
            "snapshot_id": req.snapshot_id,
            "adapter_input_id": None,
            "route": "builder_adapter_dry_run_blocked",
            "message": "Builder adapter dry run blocked because a clarification is still open. Resolve or cancel it first.",
            "blocked": True,
            "reason": "pending_clarification_blocks_adapter_dry_run",
            "router_step": "builder_adapter_dry_run",
            "adapter_status": "blocked",
            "engine_called": False,
            "excel_created": False,
            "workbook_read": False,
            "adapter_input": None,
            "validation": {"valid_for_dry_run": False, "valid_for_future_engine": False, "issues": ["Pending clarification exists"], "warnings": []},
            "state": state.model_dump(mode="json"),
            "snapshot": _snapshot_context_for_conversation(state.conversation_id),
            "adapter": None,
            "intent": "BUILDER_ADAPTER_DRY_RUN",
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderAdapterDryRunResponse.model_validate(with_no_engine_safety(payload))

    snapshot = kernel.snapshots.get(req.snapshot_id) if req.snapshot_id else kernel.snapshots.get_active(state.conversation_id)
    if not snapshot:
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": task.task_id,
            "snapshot_id": req.snapshot_id,
            "adapter_input_id": None,
            "route": "builder_adapter_dry_run_blocked",
            "message": "Builder adapter dry run blocked because no Builder snapshot exists. Create a snapshot first.",
            "blocked": True,
            "reason": "snapshot_not_found",
            "router_step": "builder_adapter_dry_run",
            "adapter_status": "blocked",
            "engine_called": False,
            "excel_created": False,
            "workbook_read": False,
            "adapter_input": None,
            "validation": {"valid_for_dry_run": False, "valid_for_future_engine": False, "issues": ["Snapshot not found"], "warnings": []},
            "state": state.model_dump(mode="json"),
            "snapshot": None,
            "adapter": None,
            "intent": "BUILDER_ADAPTER_DRY_RUN",
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderAdapterDryRunResponse.model_validate(with_no_engine_safety(payload))

    snapshot_ctx = _snapshot_context_for_conversation(state.conversation_id) or {}
    if snapshot.conversation_id != state.conversation_id:
        reason = "snapshot_conversation_mismatch"
    elif snapshot.task_id != task.task_id:
        reason = "snapshot_task_mismatch"
    elif (snapshot_ctx.get("status") or snapshot.status) != "current" and not req.allow_stale:
        reason = "snapshot_is_stale"
    else:
        reason = None

    if reason:
        payload = {
            "conversation_id": state.conversation_id,
            "active_task_id": task.task_id,
            "snapshot_id": snapshot.snapshot_id,
            "adapter_input_id": None,
            "route": "builder_adapter_dry_run_blocked",
            "message": "Builder adapter dry run blocked because the active snapshot is stale. Create a new snapshot from the current plan first." if reason == "snapshot_is_stale" else "Builder adapter dry run blocked because the snapshot does not match the active Builder task.",
            "blocked": True,
            "reason": reason,
            "router_step": "builder_adapter_dry_run",
            "adapter_status": "blocked",
            "engine_called": False,
            "excel_created": False,
            "workbook_read": False,
            "adapter_input": None,
            "validation": {"valid_for_dry_run": False, "valid_for_future_engine": False, "issues": [reason], "warnings": []},
            "state": state.model_dump(mode="json"),
            "snapshot": snapshot_ctx or snapshot.model_dump(mode="json"),
            "adapter": None,
            "adapter_dry_run": _adapter_payload_for_conversation(state.conversation_id, snapshot_ctx) if reason == "snapshot_is_stale" else None,
            "intent": "BUILDER_ADAPTER_DRY_RUN",
        }
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderAdapterDryRunResponse.model_validate(with_no_engine_safety(payload))

    result = run_builder_adapter_dry_run(snapshot=snapshot)
    payload = result.model_dump(mode="json")
    task.adapter_dry_run_result = payload
    kernel.tasks.save(task)
    kernel.adapters.save(result)
    response_payload = {
        "conversation_id": state.conversation_id,
        "active_task_id": task.task_id,
        "snapshot_id": snapshot.snapshot_id,
        "adapter_input_id": result.adapter_input_id,
        "route": "builder_adapter_dry_run",
        "message": result.message,
        "blocked": False,
        "reason": result.reason,
        "router_step": "builder_adapter_dry_run",
        "adapter_status": result.adapter_status,
        "engine_called": False,
        "excel_created": False,
        "workbook_read": False,
        "adapter_input": result.adapter_input.model_dump(mode="json"),
        "validation": result.validation.model_dump(mode="json"),
        "state": state.model_dump(mode="json"),
        "snapshot": _snapshot_context_for_conversation(state.conversation_id),
        "adapter": adapter_trace_payload(result),
        "setup_completeness": result.setup_completeness,
        "readiness": _readiness_payload_for_conversation(state.conversation_id),
        "intent": "BUILDER_ADAPTER_DRY_RUN",
    }
    _log_debug_trace(state.conversation_id, req, response_payload)
    return BuilderAdapterDryRunResponse.model_validate(with_no_engine_safety(response_payload))



def _mark_adapter_stale_for_snapshot(conversation_id: str, snapshot_id: str | None) -> None:
    if not snapshot_id:
        return
    updated = kernel.adapters.mark_snapshot_stale(snapshot_id, reason="source_snapshot_is_stale")
    if not updated:
        return
    state = kernel.conversations.get(conversation_id)
    task = kernel.tasks.get(state.active_task_id) if state else None
    if not task:
        return
    latest = kernel.adapters.get_latest(conversation_id)
    if latest and latest.snapshot_id == snapshot_id:
        task.adapter_dry_run_result = latest.model_dump(mode="json")
        kernel.tasks.save(task)


def _snapshot_context_for_conversation(conversation_id: str) -> dict | None:
    snapshot = kernel.snapshots.get_active(conversation_id)
    if not snapshot:
        return None
    state = kernel.conversations.get(conversation_id)
    task = kernel.tasks.get(state.active_task_id) if state else None
    active_plan_hash = plan_hash_from_plan(task.plan if task else {})
    if snapshot.status == "current" and snapshot.source_plan_hash and snapshot.source_plan_hash != active_plan_hash:
        snapshot = kernel.snapshots.mark_active_stale(
            conversation_id,
            reason="active_plan_changed_after_snapshot",
            active_plan_hash=active_plan_hash,
        ) or snapshot
    if snapshot.status == "stale":
        _mark_adapter_stale_for_snapshot(conversation_id, snapshot.snapshot_id)
    return {
        "snapshot_id": snapshot.snapshot_id,
        "status": snapshot.status,
        "stale_reason": snapshot.stale_reason,
        "source_plan_hash": snapshot.source_plan_hash,
        "active_plan_hash": active_plan_hash,
        "snapshot_hash": snapshot.snapshot_hash,
        "workbook_ref": public_workbook_ref(snapshot.workbook_ref),
        "setup_completeness": setup_completeness_from_snapshot(snapshot),
    }


def _adapter_payload_for_conversation(conversation_id: str, snapshot_ctx: dict | None = None) -> dict | None:
    latest_adapter = kernel.adapters.get_latest(conversation_id)
    if not latest_adapter:
        return None
    if snapshot_ctx and snapshot_ctx.get("status") == "stale" and latest_adapter.snapshot_id == snapshot_ctx.get("snapshot_id"):
        _mark_adapter_stale_for_snapshot(conversation_id, latest_adapter.snapshot_id)
        latest_adapter = kernel.adapters.get_latest(conversation_id) or latest_adapter
    payload = adapter_trace_payload(latest_adapter) or {}
    freshness = payload.get("freshness") or "current"
    return {
        "found": True,
        "adapter_input_id": latest_adapter.adapter_input_id,
        "snapshot_id": latest_adapter.snapshot_id,
        "status": payload.get("adapter_status") or latest_adapter.adapter_status,
        "freshness": freshness,
        "stale_reason": payload.get("stale_reason"),
        "engine_called": latest_adapter.engine_called,
        "excel_created": latest_adapter.excel_created,
        "workbook_read": getattr(latest_adapter, "workbook_read", False),
        "valid_for_dry_run": bool(payload.get("valid_for_dry_run", latest_adapter.validation.valid_for_dry_run)),
        "valid_for_future_engine": bool(payload.get("valid_for_future_engine", latest_adapter.validation.valid_for_future_engine)),
        "setup_completeness": payload.get("setup_completeness"),
    }


def _engine_contract_payload_for_conversation(conversation_id: str) -> dict | None:
    contract = kernel.contracts.get_latest(conversation_id)
    if contract:
        payload = contract_trace_payload(contract) or {}
        payload["replay_url"] = f"/api/builder/engine-contract/{contract.contract_id}"
        payload["boundary_audit_url"] = "/api/builder/engine-boundary-audit"
        payload["engine_boundary_audit"] = boundary_audit_summary(contract)
        return payload
    blocked = kernel.contracts.get_latest_blocked_attempt(conversation_id)
    if blocked:
        return {"found": False, "last_blocked_attempt": blocked, "engine_boundary_audit": boundary_audit_summary(None)}
    return None


def _engine_preflight_payload_for_conversation(conversation_id: str) -> dict:
    return preflight_summary(kernel.preflights.get_latest(conversation_id))


def _engine_execution_payload_for_conversation(conversation_id: str) -> dict:
    return execution_summary(kernel.executions.get_latest(conversation_id))


def _latest_workbook_read_policy_review_for_conversation(conversation_id: str) -> dict:
    """Return latest workbook-read policy review visibility from the event ledger.

    This is read-only and additive. It never opens workbooks, mutates Builder
    state, changes preview/export readiness, or enables execution.
    """
    if not conversation_id:
        return {
            "found": False,
            "status": "not_reviewed",
            "policy_only": True,
            "workbook_opened": False,
            "workbook_read": False,
            "workbook_content_read": False,
            "cells_read": False,
            "formulas_read": False,
            "engine_called": False,
            "excel_created": False,
            "legacy_builder_called": False,
        }
    for event in reversed(kernel.events.list_events(conversation_id)):
        response = event.get("response") or {}
        if response.get("route") == "builder_workbook_read_policy_review":
            return {
                "found": True,
                "status": "reviewed",
                "route": response.get("route"),
                "event_id": event.get("event_id"),
                "client_event_id": event.get("client_event_id"),
                "policy_only": True,
                "current_access_tier": response.get("current_access_tier"),
                "workbook_opened": False,
                "workbook_read": False,
                "workbook_content_read": False,
                "cells_read": False,
                "formulas_read": False,
                "engine_called": False,
                "excel_created": False,
                "legacy_builder_called": False,
                "preview_readiness_upgraded": False,
                "export_readiness_upgraded": False,
                "safety": response.get("safety") or {},
            }
    return {
        "found": False,
        "status": "not_reviewed",
        "policy_only": True,
        "workbook_opened": False,
        "workbook_read": False,
        "workbook_content_read": False,
        "cells_read": False,
        "formulas_read": False,
        "engine_called": False,
        "excel_created": False,
        "legacy_builder_called": False,
    }


def _readiness_payload_for_conversation(conversation_id: str) -> dict | None:
    state = kernel.conversations.get(conversation_id)
    if not state:
        return None
    task = kernel.tasks.get(state.active_task_id)
    workbook_read_policy = _latest_workbook_read_policy_review_for_conversation(conversation_id)
    if not task:
        return build_readiness_contract(task=None, state=state, setup={}, snapshot={}, adapter={}, engine_contract={}, normalization={}, conflicts=[], workbook_read_policy=workbook_read_policy)
    snapshot_ctx = _snapshot_context_for_conversation(conversation_id)
    adapter_payload = _adapter_payload_for_conversation(conversation_id, snapshot_ctx)
    contract_payload = _engine_contract_payload_for_conversation(conversation_id) or {}
    setup = setup_completeness_from_plan(
        plan=task.plan or {},
        workbook_ref=task.workbook,
        pending_clarification=bool(task.pending_clarification),
        snapshot_status=(snapshot_ctx or {}).get("status") if snapshot_ctx else None,
        adapter_freshness=(adapter_payload or {}).get("freshness") if adapter_payload else None,
    )
    normalization = plan_normalization_report(task.plan or {})
    return build_readiness_contract(
        task=task,
        state=state,
        setup=setup,
        snapshot={"found": bool(snapshot_ctx), **(snapshot_ctx or {})},
        adapter=adapter_payload or {},
        engine_contract=contract_payload,
        engine_boundary_audit=(contract_payload or {}).get("engine_boundary_audit") or {},
        normalization=normalization,
        conflicts=[],
        workbook_read_policy=workbook_read_policy,
    )


def _missing_required_from_response(payload: dict) -> list[str]:
    setup = payload.get("setup_completeness") or {}
    missing = list(setup.get("missing_required") or [])
    validation = payload.get("validation") or {}
    for blocker in validation.get("blockers") or []:
        for field in blocker.get("fields") or []:
            if field not in missing:
                missing.append(field)
    return missing


def _contract_block_payload(
    *,
    state,
    task=None,
    req: BuilderEngineContractRequest,
    reason: str,
    message: str,
    validation: dict | None = None,
    snapshot=None,
    snapshot_ctx: dict | None = None,
    adapter=None,
    contract=None,
    setup_completeness: dict | None = None,
) -> dict:
    validation = validation or {"valid": False, "issues": [reason], "warnings": [], "blockers": []}
    payload = {
        "conversation_id": state.conversation_id if state else req.conversation_id,
        "active_task_id": task.task_id if task else None,
        "snapshot_id": (snapshot.snapshot_id if snapshot else req.snapshot_id),
        "adapter_input_id": adapter.adapter_input_id if adapter else req.adapter_input_id,
        "contract_id": None,
        "route": "builder_engine_contract_blocked",
        "message": message,
        "contract_created": False,
        "blocked": True,
        "reason": reason,
        "router_step": "builder_engine_contract",
        "contract_status": "blocked",
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract": contract.model_dump(mode="json") if hasattr(contract, "model_dump") else contract,
        "validation": validation,
        "state": state.model_dump(mode="json") if state else {},
        "snapshot": snapshot_ctx or (snapshot.model_dump(mode="json") if hasattr(snapshot, "model_dump") else snapshot),
        "adapter": adapter_trace_payload(adapter) if adapter else None,
        "engine_contract": contract_trace_payload(contract) if contract else None,
        "setup_completeness": setup_completeness or (getattr(contract, "setup_completeness", None) if contract else None),
        "readiness": _readiness_payload_for_conversation(state.conversation_id if state else req.conversation_id) if state else None,
        "intent": "BUILDER_ENGINE_CONTRACT",
    }
    payload["missing_required"] = _missing_required_from_response(payload)
    return payload


@app.post("/api/builder/engine-contract", response_model=BuilderEngineContractResponse)
def api_builder_engine_contract(req: BuilderEngineContractRequest) -> BuilderEngineContractResponse:
    state = kernel.conversations.get(req.conversation_id)
    if not state:
        payload = _contract_block_payload(
            state=None,
            req=req,
            reason="conversation_not_found",
            message="Builder engine contract blocked because the conversation was not found.",
            validation={"valid": False, "issues": ["conversation_not_found"], "warnings": [], "blockers": [{"code": "conversation_not_found", "message": "Conversation was not found.", "fields": ["conversation_id"]}]},
        )
        _log_debug_trace(req.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    task = kernel.tasks.get(state.active_task_id)
    if not task or task.tool != "builder":
        payload = _contract_block_payload(
            state=state,
            task=task,
            req=req,
            reason="no_active_builder_task",
            message="Builder engine contract blocked because there is no active Builder task.",
            validation={"valid": False, "issues": ["no_active_builder_task"], "warnings": [], "blockers": [{"code": "no_active_builder_task", "message": "No active Builder task exists.", "fields": ["active_task_id"]}]},
        )
        kernel.contracts.save_blocked_attempt(state.conversation_id, payload)
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    if task.pending_clarification or state.pending_clarification_id:
        payload = _contract_block_payload(
            state=state,
            task=task,
            req=req,
            reason="pending_clarification_exists",
            message="Builder engine contract blocked because a clarification is still open. Resolve or cancel it first.",
            validation={"valid": False, "issues": ["pending_clarification_exists"], "warnings": [], "blockers": [{"code": "pending_clarification_exists", "message": "Resolve or cancel the pending clarification first.", "fields": ["pending_clarification"]}]},
            snapshot_ctx=_snapshot_context_for_conversation(state.conversation_id),
            adapter=kernel.adapters.get_latest(state.conversation_id),
        )
        payload["pending_clarification_id"] = state.pending_clarification_id
        kernel.contracts.save_blocked_attempt(state.conversation_id, payload)
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    snapshot = kernel.snapshots.get(req.snapshot_id) if req.snapshot_id else kernel.snapshots.get_active(state.conversation_id)
    snapshot_ctx = _snapshot_context_for_conversation(state.conversation_id) if snapshot else None
    if not snapshot:
        payload = _contract_block_payload(
            state=state,
            task=task,
            req=req,
            reason="snapshot_not_found",
            message="Builder engine contract blocked because no current Builder snapshot exists. Create a snapshot first.",
            validation={"valid": False, "issues": ["snapshot_not_found"], "warnings": [], "blockers": [{"code": "snapshot_not_found", "message": "Create a Builder snapshot before creating an engine contract.", "fields": ["snapshot_id"]}]},
        )
        kernel.contracts.save_blocked_attempt(state.conversation_id, payload)
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    if snapshot.conversation_id != state.conversation_id or snapshot.task_id != task.task_id:
        reason = "snapshot_task_mismatch"
    elif (snapshot_ctx or {}).get("status", snapshot.status) != "current" and not req.allow_stale:
        reason = "snapshot_is_stale"
    else:
        reason = None
    if reason:
        payload = _contract_block_payload(
            state=state,
            task=task,
            req=req,
            reason=reason,
            message="Builder engine contract blocked because the Builder snapshot is stale or does not match the active task.",
            validation={"valid": False, "issues": [reason], "warnings": [], "blockers": [{"code": reason, "message": "Create a new current snapshot before creating an engine contract.", "fields": ["snapshot_id"]}]},
            snapshot=snapshot,
            snapshot_ctx=snapshot_ctx,
            adapter=kernel.adapters.get_latest(state.conversation_id),
        )
        kernel.contracts.save_blocked_attempt(state.conversation_id, payload)
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    adapter = kernel.adapters.get(req.adapter_input_id) if req.adapter_input_id else kernel.adapters.get_latest(state.conversation_id)
    if adapter and adapter.snapshot_id != snapshot.snapshot_id:
        payload = _contract_block_payload(
            state=state,
            task=task,
            req=req,
            reason="adapter_is_stale",
            message="Builder engine contract blocked because the latest adapter dry run was created from a different snapshot. Run adapter dry run again.",
            validation={"valid": False, "issues": ["adapter_is_stale"], "warnings": [], "blockers": [{"code": "adapter_is_stale", "message": "Run adapter dry run again for the current snapshot.", "fields": ["adapter_input_id", "snapshot_id"]}], "stale_reason": "adapter_snapshot_mismatch"},
            snapshot=snapshot,
            snapshot_ctx=snapshot_ctx,
            adapter=adapter,
        )
        kernel.contracts.save_blocked_attempt(state.conversation_id, payload)
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    if not adapter:
        payload = _contract_block_payload(
            state=state,
            task=task,
            req=req,
            reason="adapter_required",
            message="Builder engine contract blocked because a current adapter dry run is required. Run adapter dry run first.",
            validation={"valid": False, "issues": ["adapter_required"], "warnings": [], "blockers": [{"code": "adapter_required", "message": "Run adapter dry run before creating an engine contract.", "fields": ["adapter_input_id"]}]},
            snapshot=snapshot,
            snapshot_ctx=snapshot_ctx,
        )
        kernel.contracts.save_blocked_attempt(state.conversation_id, payload)
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    if adapter.freshness != "current" and not req.allow_stale:
        payload = _contract_block_payload(
            state=state,
            task=task,
            req=req,
            reason="adapter_is_stale",
            message="Builder engine contract blocked because the latest adapter dry run is stale. Run adapter dry run again.",
            validation={"valid": False, "issues": ["adapter_is_stale"], "warnings": [], "blockers": [{"code": "adapter_is_stale", "message": "Run adapter dry run again before creating an engine contract.", "fields": ["adapter_input_id"]}]},
            snapshot=snapshot,
            snapshot_ctx=snapshot_ctx,
            adapter=adapter,
        )
        kernel.contracts.save_blocked_attempt(state.conversation_id, payload)
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    contract = create_builder_engine_contract(snapshot=snapshot, adapter=adapter)
    if not contract.validation.valid:
        reason = contract.validation.issues[0] if contract.validation.issues else "contract_validation_failed"
        if "setup_conflict_unresolved" in contract.validation.issues or "normalization_needs_clarification" in contract.validation.issues:
            reason = "setup_conflict_unresolved"
        elif "setup_not_ready_for_future_engine" in contract.validation.issues:
            reason = "setup_not_ready_for_future_engine"
        payload = _contract_block_payload(
            state=state,
            task=task,
            req=req,
            reason=reason,
            message="Builder engine contract blocked because setup is not ready for future engine connection.",
            validation=contract.validation.model_dump(mode="json"),
            snapshot=snapshot,
            snapshot_ctx=snapshot_ctx,
            adapter=adapter,
            contract=contract,
            setup_completeness=contract.setup_completeness,
        )
        kernel.contracts.save_blocked_attempt(state.conversation_id, payload)
        _log_debug_trace(state.conversation_id, req, payload)
        return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))

    kernel.contracts.save(contract)
    replay_url = f"/api/builder/engine-contract/{contract.contract_id}"
    payload = {
        "conversation_id": state.conversation_id,
        "active_task_id": task.task_id,
        "snapshot_id": snapshot.snapshot_id,
        "adapter_input_id": adapter.adapter_input_id,
        "contract_id": contract.contract_id,
        "route": "builder_engine_contract_created",
        "message": "Builder engine contract created. No Builder engine was called and no Excel file was created.",
        "contract_created": True,
        "replay_url": replay_url,
        "blocked": False,
        "reason": "contract_created_from_adapter_dry_run",
        "router_step": "builder_engine_contract",
        "contract_status": contract.contract_status,
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract": contract.model_dump(mode="json"),
        "validation": contract.validation.model_dump(mode="json"),
        "state": state.model_dump(mode="json"),
        "snapshot": snapshot_ctx or snapshot.model_dump(mode="json"),
        "adapter": adapter_trace_payload(adapter),
        "engine_contract": contract_trace_payload(contract),
        "setup_completeness": contract.setup_completeness,
        "readiness": _readiness_payload_for_conversation(state.conversation_id),
        "intent": "BUILDER_ENGINE_CONTRACT",
    }
    _log_debug_trace(state.conversation_id, req, payload)
    return BuilderEngineContractResponse.model_validate(with_no_engine_safety(payload))


@app.get("/api/builder/engine-contract/latest/{conversation_id}")
def api_builder_engine_contract_latest(conversation_id: str) -> dict:
    contract = kernel.contracts.get_latest(conversation_id)
    if not contract:
        return with_no_engine_safety({
            "found": False,
            "route": "builder_engine_contract_latest_not_found",
            "conversation_id": conversation_id,
            "reason": "contract_not_found",
            "last_blocked_attempt": kernel.contracts.get_latest_blocked_attempt(conversation_id),
            "engine_boundary_audit": boundary_audit_summary(None),
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "legacy_builder_called": False,
        })
    payload = contract_trace_payload(contract) or {}
    payload.update({
        "route": "builder_engine_contract_latest_replay",
        "conversation_id": conversation_id,
        "contract_schema_version": contract.contract_schema_version,
        "legacy_target": contract.legacy_target,
        "engine_boundary_audit": boundary_audit_summary(contract),
        "contract": contract.model_dump(mode="json"),
    })
    return with_no_engine_safety(payload)


@app.get("/api/builder/engine-contract/{contract_id}")
def api_builder_engine_contract_replay(contract_id: str) -> dict:
    contract = kernel.contracts.get(contract_id)
    if not contract:
        return with_no_engine_safety({
            "found": False,
            "route": "builder_engine_contract_replay_not_found",
            "contract_id": contract_id,
            "blocked": True,
            "reason": "contract_not_found",
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "legacy_builder_called": False,
            "engine_boundary_audit": boundary_audit_summary(None),
        })
    return with_no_engine_safety({
        "found": True,
        "route": "builder_engine_contract_replay",
        "contract_id": contract.contract_id,
        "contract_status": contract.contract_status,
        "contract_schema_version": contract.contract_schema_version,
        "legacy_target": contract.legacy_target,
        "contract_only": contract.safety.contract_only,
        "legacy_builder_called": contract.safety.legacy_builder_called,
        "workbook_read": contract.safety.workbook_read,
        "engine_called": contract.safety.engine_called,
        "excel_created": contract.safety.excel_created,
        "contract": contract.model_dump(mode="json"),
        "validation": contract.validation.model_dump(mode="json"),
        "engine_boundary_audit": boundary_audit_summary(contract),
    })


@app.post("/api/builder/contract-fixture-replay")
def api_builder_contract_fixture_replay(payload: dict | None = None) -> dict:
    """Replay and diff saved Builder engine contract fixtures without execution.

    This endpoint is intentionally contract-only. It never calls the legacy
    Builder, never reads workbook contents, and never creates Excel output.
    """
    payload = payload or {}
    conversation_id = payload.get("conversation_id") or "contract_fixture_replay"
    fixture = payload.get("fixture") or "wall_types_xgetwallarea_zone1_head2_gf_l3_contract_v1"
    contract_id = payload.get("contract_id")
    contract = kernel.contracts.get(contract_id) if contract_id else kernel.contracts.get_latest(conversation_id)
    result = run_contract_fixture_replay(
        fixture=fixture,
        conversation_id=conversation_id,
        contract=contract,
        write_report=bool(payload.get("write_report", True)),
        intentional_mismatch=bool(payload.get("intentional_mismatch", False)),
    )
    result["readiness"] = _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, type("FixtureReplayRequest", (), {"client_event_id": payload.get("client_event_id"), "model_dump": lambda self, mode="json": payload})(), result)
    return with_no_engine_safety(result)


@app.post("/api/builder/legacy-bridge-shadow-probe", response_model=LegacyBridgeShadowProbeResponse)
def api_builder_legacy_bridge_shadow_probe(req: LegacyBridgeShadowProbeRequest) -> LegacyBridgeShadowProbeResponse:
    """Metadata-only readiness probe for the future legacy Builder bridge.

    This endpoint does not import or call the legacy Builder, does not read
    workbook contents, and does not create preview rows or Excel output.
    """
    state = kernel.conversations.get_or_create(req.conversation_id)
    conversation_id = state.conversation_id
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(conversation_id)
    result = run_legacy_bridge_shadow_probe(
        conversation_id=conversation_id,
        client_event_id=req.client_event_id,
        contract=contract,
        allow_missing_contract=req.allow_missing_contract,
    )
    result["readiness"] = _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, req, result)
    return LegacyBridgeShadowProbeResponse.model_validate(with_no_engine_safety(result))


@app.post("/api/builder/preview-execution-policy", response_model=PreviewExecutionPolicyResponse)
def api_builder_preview_execution_policy(req: PreviewExecutionPolicyRequest) -> PreviewExecutionPolicyResponse:
    """Metadata-only workbook access and preview/export execution policy.

    This endpoint does not read workbook files, does not resolve executable
    filesystem paths, does not import/call the legacy Builder, does not enqueue
    jobs, and does not create preview rows, formulas, manifests, or Excel files.
    """
    state = kernel.conversations.get_or_create(req.conversation_id)
    conversation_id = state.conversation_id
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(conversation_id)
    result = evaluate_preview_execution_policy(
        conversation_id=conversation_id,
        client_event_id=req.client_event_id,
        contract=contract,
        requested_action=req.requested_action,
    )
    result["readiness"] = _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, req, result)
    return PreviewExecutionPolicyResponse.model_validate(with_no_engine_safety(result))




@app.post("/api/builder/safe-workbook-path-resolver-dry-run", response_model=SafeWorkbookPathResolverDryRunResponse)
def api_builder_safe_workbook_path_resolver_dry_run(req: SafeWorkbookPathResolverDryRunRequest) -> SafeWorkbookPathResolverDryRunResponse:
    """Metadata-only safe workbook path resolver dry run.

    This endpoint reads only Jarvis metadata store contract data. It does not
    resolve filesystem paths, check workbook file existence, open workbooks,
    parse workbooks, call the Builder engine, call the legacy Builder, enqueue
    jobs, generate formulas, or create Excel output.
    """
    state = kernel.conversations.get_or_create(req.conversation_id)
    conversation_id = state.conversation_id
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(conversation_id)
    result = evaluate_safe_workbook_path_resolver_dry_run(
        conversation_id=conversation_id,
        client_event_id=req.client_event_id,
        contract=contract,
    )
    result["readiness"] = _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, req, result)
    return SafeWorkbookPathResolverDryRunResponse.model_validate(with_no_engine_safety(result))

@app.post("/api/builder/workbook-read-preflight-dry-run", response_model=WorkbookReadPreflightDryRunResponse)
def api_builder_workbook_read_preflight_dry_run(req: WorkbookReadPreflightDryRunRequest) -> WorkbookReadPreflightDryRunResponse:
    """Metadata-only workbook read preflight contract dry run.

    This endpoint reads only Jarvis metadata store contract data. It may reuse
    the alpha.29 safe path resolver metadata result, but it never resolves,
    checks, opens, parses, or reads workbook files.
    """
    state = kernel.conversations.get_or_create(req.conversation_id)
    conversation_id = state.conversation_id
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(conversation_id)
    result = evaluate_workbook_read_preflight_dry_run(
        conversation_id=conversation_id,
        client_event_id=req.client_event_id,
        contract=contract,
    )
    result["readiness"] = _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, req, result)
    return WorkbookReadPreflightDryRunResponse.model_validate(with_no_engine_safety(result))


@app.post("/api/builder/workbook-metadata-probe-approval", response_model=WorkbookMetadataProbeApprovalResponse)
def api_builder_workbook_metadata_probe_approval(req: WorkbookMetadataProbeApprovalRequest) -> WorkbookMetadataProbeApprovalResponse:
    """User-facing workbook metadata probe approval contract.

    This endpoint reads only already-stored Jarvis contract/workbook_ref metadata.
    It never opens, parses, reads, resolves, stats, or inspects workbook files,
    and it never upgrades preview/export readiness.
    """
    state = kernel.conversations.get_or_create(req.conversation_id)
    conversation_id = state.conversation_id
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(conversation_id)
    result = evaluate_workbook_metadata_probe_approval(
        conversation_id=conversation_id,
        client_event_id=req.client_event_id,
        contract=contract,
        approval_granted=req.approval_granted,
    )
    result["readiness"] = result.get("readiness") or _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, req, result)
    return WorkbookMetadataProbeApprovalResponse.model_validate(with_no_engine_safety(result))


@app.post("/api/builder/workbook-sheet-name-probe-approval", response_model=WorkbookSheetNameProbeApprovalResponse)
def api_builder_workbook_sheet_name_probe_approval(req: WorkbookSheetNameProbeApprovalRequest) -> WorkbookSheetNameProbeApprovalResponse:
    """User-facing workbook sheet-name probe approval contract.

    This wrapper delegates all sheet-name probe logic to the single alpha.34
    owner module. It does not mutate Builder plans, snapshots, adapters,
    contracts, preflight, preview, export, or output state.
    """
    state = kernel.conversations.get_or_create(req.conversation_id)
    conversation_id = state.conversation_id
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(conversation_id)
    result = evaluate_workbook_sheet_name_probe_approval(
        conversation_id=conversation_id,
        client_event_id=req.client_event_id,
        contract=contract,
        approval_granted=req.approval_granted,
    )
    result["readiness"] = result.get("readiness") or _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, req, result)
    return WorkbookSheetNameProbeApprovalResponse.model_validate(with_no_engine_safety(result))


@app.post("/api/builder/workbook-read-policy-review", response_model=WorkbookReadPolicyReviewResponse)
def api_builder_workbook_read_policy_review(req: WorkbookReadPolicyReviewRequest) -> WorkbookReadPolicyReviewResponse:
    """Workbook-read policy review contract.

    This endpoint returns policy metadata only. It does not open workbooks,
    inspect workbook files, mutate Builder state, or upgrade preview/export
    readiness.
    """
    state = kernel.conversations.get_or_create(req.conversation_id)
    conversation_id = state.conversation_id
    result = evaluate_workbook_read_policy_review(
        conversation_id=conversation_id,
        client_event_id=req.client_event_id,
    )
    result["readiness"] = result.get("readiness") or _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, req, result)
    return WorkbookReadPolicyReviewResponse.model_validate(with_no_engine_safety(result))


@app.post("/api/builder/legacy-import-boundary-audit")
def api_builder_legacy_import_boundary_audit(payload: dict | None = None) -> dict:
    """Audit the legacy Builder import boundary without importing or calling it."""
    payload = payload or {}
    conversation_id = payload.get("conversation_id") or "legacy_import_boundary_audit"
    state = kernel.conversations.get_or_create(conversation_id)
    conversation_id = state.conversation_id
    result = run_legacy_import_boundary_audit(
        conversation_id=conversation_id,
        client_event_id=payload.get("client_event_id"),
        write_report=bool(payload.get("write_report", True)),
    )
    result["readiness"] = _readiness_payload_for_conversation(conversation_id)
    _log_debug_trace(conversation_id, type("LegacyImportBoundaryAuditRequest", (), {"client_event_id": payload.get("client_event_id"), "model_dump": lambda self, mode="json": payload})(), result)
    return with_no_engine_safety(result)


@app.get("/api/builder/legacy-import-boundary-audit/latest/{conversation_id}")
def api_builder_legacy_import_boundary_audit_latest(conversation_id: str) -> dict:
    return with_no_engine_safety(latest_legacy_import_boundary_audit(conversation_id))


@app.post("/api/builder/engine-preflight", response_model=BuilderEnginePreflightResponse)
def api_builder_engine_preflight(req: BuilderEnginePreflightRequest) -> BuilderEnginePreflightResponse:
    state = kernel.conversations.get(req.conversation_id)
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(req.conversation_id)
    pending = False
    if state:
        task = kernel.tasks.get(state.active_task_id) if state.active_task_id else None
        pending = bool((task and task.pending_clarification) or state.pending_clarification_id)
    if pending:
        payload = {
            "conversation_id": req.conversation_id,
            "contract_id": contract.contract_id if contract else None,
            "preflight_id": None,
            "route": "builder_engine_preflight_blocked",
            "message": "Builder engine preflight blocked because a clarification is still open. Resolve or cancel it first.",
            "blocked": True,
            "reason": "pending_clarification_exists",
            "preflight_status": "blocked",
            "contract_schema_version": getattr(contract, "contract_schema_version", "builder_contract_v1"),
            "legacy_target": getattr(contract, "legacy_target", "legacy_builder_v4_contract_v1"),
            "compatibility": {"valid": False, "score": 0, "missing_required_fields": [], "ambiguous_fields": [], "warnings": [], "issues": ["pending_clarification_exists"]},
            "safety": {"workbook_read": False, "engine_called": False, "excel_created": False, "contract_only": True, "legacy_builder_called": False},
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "contract_only": True,
            "legacy_builder_called": False,
            "contract": contract.model_dump(mode="json") if contract else None,
            "engine_boundary_audit": boundary_audit_summary(contract),
            "validation": {"valid": False, "issues": ["pending_clarification_exists"], "warnings": []},
            "readiness": _readiness_payload_for_conversation(req.conversation_id),
        }
        _log_debug_trace(req.conversation_id, req, payload)
        return BuilderEnginePreflightResponse.model_validate(with_no_engine_safety(payload))

    payload = run_engine_preflight(contract, export_fixture=req.export_fixture)
    payload["conversation_id"] = req.conversation_id
    payload["readiness"] = _readiness_payload_for_conversation(req.conversation_id)
    if payload.get("preflight_id"):
        kernel.preflights.save(payload)
    _log_debug_trace(req.conversation_id, req, payload)
    return BuilderEnginePreflightResponse.model_validate(with_no_engine_safety(payload))


@app.post("/api/builder/engine-execution-request", response_model=BuilderEngineExecutionResponse)
def api_builder_engine_execution_request(req: BuilderEngineExecutionRequest) -> BuilderEngineExecutionResponse:
    state = kernel.conversations.get(req.conversation_id)
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(req.conversation_id)
    preflight = kernel.preflights.get(req.preflight_id) if req.preflight_id else kernel.preflights.get_latest(req.conversation_id)
    pending = False
    if state:
        task = kernel.tasks.get(state.active_task_id) if state.active_task_id else None
        pending = bool((task and task.pending_clarification) or state.pending_clarification_id)
    payload = prepare_legacy_builder_execution_request(
        conversation_id=req.conversation_id,
        contract=contract,
        preflight=preflight,
        pending_clarification=pending,
    )
    payload["readiness"] = _readiness_payload_for_conversation(req.conversation_id)
    if payload.get("execution_request_id"):
        kernel.executions.save(payload)
    _log_debug_trace(req.conversation_id, req, payload)
    return BuilderEngineExecutionResponse.model_validate(with_no_engine_safety(payload))


@app.post("/api/builder/engine-boundary-audit", response_model=BuilderEngineBoundaryAuditResponse)
def api_builder_engine_boundary_audit(req: BuilderEngineBoundaryAuditRequest) -> BuilderEngineBoundaryAuditResponse:
    contract = kernel.contracts.get(req.contract_id) if req.contract_id else kernel.contracts.get_latest(req.conversation_id)
    audit = audit_builder_engine_boundary(contract)
    payload = {
        "conversation_id": req.conversation_id,
        **audit,
        "contract": contract.model_dump(mode="json") if contract else None,
        "engine_boundary_audit": boundary_audit_summary(contract),
        "readiness": _readiness_payload_for_conversation(req.conversation_id),
        "intent": "BUILDER_ENGINE_BOUNDARY_AUDIT",
    }
    _log_debug_trace(req.conversation_id, req, payload)
    return BuilderEngineBoundaryAuditResponse.model_validate(with_no_engine_safety(payload))


@app.get("/api/debug/pending-clarification/{conversation_id}")
def api_debug_pending_clarification(conversation_id: str) -> dict:
    state = kernel.conversations.get(conversation_id)
    if not state:
        return {"found": False, "conversation_id": conversation_id, "reason": "conversation_not_found"}
    task = kernel.tasks.get(state.active_task_id)
    pending = task.pending_clarification if task else None
    return {
        "found": bool(pending),
        "conversation_id": state.conversation_id,
        "active_task_id": task.task_id if task else None,
        "pending_clarification_id": state.pending_clarification_id,
        "pending_clarification": pending,
    }


@app.get("/api/debug/router-trace/{conversation_id}")
def api_debug_router_trace(conversation_id: str) -> dict:
    return {
        "conversation_id": conversation_id,
        "trace": kernel.events.router_trace(conversation_id),
    }


@app.get("/api/state/{conversation_id}")
def api_state(conversation_id: str) -> dict:
    state = kernel.conversations.get(conversation_id)
    if not state:
        return {"found": False, "conversation_id": conversation_id}
    task = kernel.tasks.get(state.active_task_id)
    return {
        "found": True,
        "conversation": state.model_dump(mode="json"),
        "active_task": task.model_dump(mode="json") if task else None,
    }


@app.get("/api/plan/{conversation_id}")
def api_plan(conversation_id: str) -> dict:
    state = kernel.conversations.get(conversation_id)
    if not state:
        return no_active_task_plan_payload(conversation_id, "conversation_not_found")
    task = kernel.tasks.get(state.active_task_id)
    if not task:
        return no_active_task_plan_payload(state.conversation_id, "no_active_task")
    snapshot_ctx = _snapshot_context_for_conversation(state.conversation_id)
    adapter_payload = _adapter_payload_for_conversation(state.conversation_id, snapshot_ctx)
    setup = setup_completeness_from_plan(
        plan=task.plan or {},
        workbook_ref=task.workbook,
        pending_clarification=bool(task.pending_clarification),
        snapshot_status=(snapshot_ctx or {}).get("status") if snapshot_ctx else None,
        adapter_freshness=(adapter_payload or {}).get("freshness") if adapter_payload else None,
    )
    engine_contract_payload = _engine_contract_payload_for_conversation(state.conversation_id) or {"found": False}
    workbook_read_policy = _latest_workbook_read_policy_review_for_conversation(state.conversation_id)
    if isinstance(engine_contract_payload, dict) and "contract_status" not in engine_contract_payload and "status" in engine_contract_payload:
        engine_contract_payload = dict(engine_contract_payload)
        engine_contract_payload["contract_status"] = engine_contract_payload.get("status")
    normalization = plan_normalization_report(task.plan or {})
    readiness = build_readiness_contract(
        task=task,
        state=state,
        setup=setup,
        snapshot={"found": bool(snapshot_ctx), **(snapshot_ctx or {})},
        adapter=adapter_payload or {},
        engine_contract=engine_contract_payload,
        engine_boundary_audit=(engine_contract_payload or {}).get("engine_boundary_audit") or {},
        normalization=normalization,
        conflicts=[],
        workbook_read_policy=workbook_read_policy,
    )
    engine_preflight_payload = _engine_preflight_payload_for_conversation(state.conversation_id)
    engine_execution_payload = _engine_execution_payload_for_conversation(state.conversation_id)
    latest_fixture_replay = None
    try:
        from jarvis_app.tools.builder.contract_fixture_replay import latest_fixture_replay_summary
        latest_fixture_replay = latest_fixture_replay_summary(state.conversation_id)
    except Exception:
        latest_fixture_replay = {"found": False}
    active_task_payload = {
        "found": True,
        "task_id": task.task_id,
        "tool": task.tool,
        "status": task.status,
        "workbook_found": bool(task.workbook),
        "pending_clarification": bool(task.pending_clarification),
    }
    snapshot_payload = {"found": bool(snapshot_ctx), **(snapshot_ctx or {})}
    adapter_dry_run_payload = adapter_payload or {"found": False}
    payload = {
        "found": True,
        "version": APP_VERSION,
        "conversation_id": state.conversation_id,
        "active_task_id": task.task_id,
        "tool": task.tool,
        "status": task.status,
        "active_task": active_task_payload,
        "plan_summary": plan_summary(task.plan or {}),
        "workbook": {"found": bool(task.workbook), **(public_workbook_ref(task.workbook) or {})},
        "snapshot": snapshot_payload,
        "adapter_dry_run": adapter_dry_run_payload,
        "engine_contract": engine_contract_payload,
        "latest_snapshot": snapshot_payload,
        "latest_adapter": adapter_dry_run_payload,
        "latest_engine_contract": engine_contract_payload,
        "engine_boundary_audit": (engine_contract_payload or {}).get("engine_boundary_audit") or boundary_audit_summary(None),
        "engine_preflight": engine_preflight_payload,
        "engine_execution": engine_execution_payload,
        "workbook_read_policy": workbook_read_policy,
        "contract_fixture_replay": latest_fixture_replay or {"found": False},
        "legacy_import_boundary_audit": latest_legacy_import_boundary_audit_summary(state.conversation_id),
        "setup_completeness": setup,
        "normalization": normalization,
        "conflicts": [],
        "readiness": readiness,
    }
    return payload


@app.post("/api/dev/validate-test-pack")
def api_dev_validate_test_pack(payload: dict | None = None) -> dict:
    """Validate an imported test pack before execution.

    Returns clean structured errors for missing/bad JSON/bad schema packs and
    compatibility warnings for likely AI-generated route/assertion mistakes.
    No Builder, Formatter, QA, workbook parser, or Excel engine is called.
    """
    payload = payload or {}
    pack = payload.get("pack") or "alpha11_contract_negative_guards"
    try:
        loaded = load_test_pack(pack)
    except TestPackLoadError as exc:
        body = exc.to_response()
        body["route"] = "dev_test_pack_invalid"
        raise HTTPException(status_code=422, detail=body)
    result = validate_loaded_pack(loaded)
    result.update({
        "route": "dev_test_pack_validated",
        "version": APP_VERSION,
        "pack": loaded.pack_name,
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
    })
    return result


@app.post("/api/dev/run-smoke-tests")
def api_dev_run_smoke_tests(payload: dict | None = None) -> dict:
    """Run local dev-only API test packs without connecting any engine.

    This endpoint uses FastAPI TestClient against the current app instance. It
    exists for local alpha testing only and must not call Builder export,
    workbook parsing, Formatter, QA, O&A, or any destructive endpoint.
    Invalid imported packs return structured 422 errors instead of raw 500.
    """
    payload = payload or {}
    pack = payload.get("pack") or "alpha11_contract_negative_guards"
    write_report = bool(payload.get("write_report", True))
    with TestPackExecutor(app, write_report=write_report) as executor:
        result = executor.run_pack(pack)
    result["route"] = "dev_smoke_tests_completed" if result.get("overall") != "INVALID_PACK" else "dev_test_pack_invalid"
    result["workbook_read"] = False
    result["engine_called"] = False
    result["excel_created"] = False
    result["contract_only"] = True
    result["legacy_builder_called"] = False
    if result.get("overall") == "INVALID_PACK":
        raise HTTPException(status_code=422, detail=result)
    return result


@app.get("/api/events/{conversation_id}")
def api_events(conversation_id: str) -> dict:
    return {
        "conversation_id": conversation_id,
        "events": kernel.events.list_events(conversation_id),
    }
