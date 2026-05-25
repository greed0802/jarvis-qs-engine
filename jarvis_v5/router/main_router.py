from __future__ import annotations

from typing import Any
from jarvis_v5.core.state_kernel import StateKernel
from jarvis_v5.config import APP_VERSION
from jarvis_v5.router.route_context import build_route_context, RouteContext
from jarvis_v5.router.clarification_gate import handle_pending_clarification
from jarvis_v5.router.feedback_router import handle_feedback, is_explicit_standalone_feedback, is_active_task_issue_feedback
from jarvis_v5.router.intent_classifier import classify_intent
from jarvis_v5.reducers.slot_reducer import apply_slot_edit, looks_like_slot_edit_text
from jarvis_v5.schemas.builder_plan_schema import default_builder_shell_plan, plan_summary
from jarvis_v5.schemas.builder_snapshot_schema import plan_hash_from_plan
from jarvis_v5.schemas.message_schema import ChatRequest, ChatResponse
from jarvis_v5.tools.builder.adapter_dry_run import adapter_trace_payload
from jarvis_v5.tools.builder.engine_contract_adapter import contract_trace_payload
from jarvis_v5.tools.builder.setup_completeness import setup_completeness_from_plan
from jarvis_v5.parsers.conflict_guard import plan_normalization_report
from jarvis_v5.tools.builder.engine_boundary_audit import boundary_audit_summary
from jarvis_v5.tools.builder.engine_preflight import preflight_summary
from jarvis_v5.router.qs_intent_aliases import is_explicit_new_task_request
from jarvis_v5.router.no_active_task_language_gate import NoActiveTaskLanguageDecision, classify_no_active_task_language, detect_workbook_read_policy_review
from jarvis_v5.router.active_task_language_gate import is_active_task_non_mutating_language, is_explicit_setup_command_text, detect_active_task_content_read_attack
from jarvis_v5.tools.builder.legacy_engine_bridge import execution_summary
from jarvis_v5.core.readiness_contract import build_readiness_contract, build_review_message
from jarvis_v5.router.router_confidence_engine import score_route_candidates, attach_actual_route, confidence_engine_can_control
from jarvis_v5.registry.registry_loader import route_capability_diagnostics, requirement_check
from jarvis_v5.tools.builder.workbook_read_policy_review import evaluate_workbook_read_policy_review


def public_workbook_ref(workbook: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return workbook metadata safe for normal API/review display.

    The saved_path stays in internal state/debug endpoints only. Alpha.6 does
    not read or inspect the workbook.
    """
    if not isinstance(workbook, dict):
        return None
    workbook_id = workbook.get("workbook_id") or workbook.get("attachment_id")
    return {
        "workbook_id": workbook_id,
        "attachment_id": workbook.get("attachment_id") or workbook_id,
        "filename": workbook.get("filename"),
        "content_type": workbook.get("content_type"),
        "size_bytes": workbook.get("size_bytes"),
        "source": workbook.get("source") or "upload",
        "bound_to_task_id": workbook.get("bound_to_task_id"),
        "created_at": workbook.get("created_at"),
    }


def _active_action_diagnostic_payload(action: str | None, route: str | None, *, exact: bool = False, natural_payload: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Return additive active-action diagnostics without changing routing.

    Alpha.31F.1 compatibility: exact active action aliases already routed
    correctly, but older weakness packs expect active_task_action_language.matched
    to be present for both exact and natural active actions.
    """
    if exact is False and isinstance(natural_payload, dict):
        return natural_payload
    if not action:
        return None
    route_hint = route or {
        "review": "active_task_review",
        "preview": "active_task_preview_stub",
        "export": "active_task_export_stub",
        "download": "active_task_action_stub",
        "cancel": "active_task_cancelled",
        "cancel_task": "active_task_cancelled",
        "start_new": "active_task_start_new",
        "approve_preview": "active_task_preview_stub",
    }.get(action, "active_task_action_stub")
    reason = "active_task_exact_action_alias" if exact else "active_task_action_language"
    payload = {
        "matched": True,
        "action": action,
        "route_hint": route_hint,
        "confidence": 100 if exact else 96,
        "reason": reason,
    }
    if exact:
        payload["alias"] = f"exact_{action}"
    return payload


def _active_action_route_meta(action: str | None, route: str, task, *, exact: bool, active_action_language=None) -> dict[str, Any]:
    natural_payload = active_action_language.as_dict() if active_action_language else None
    diagnostic = _active_action_diagnostic_payload(action, route, exact=exact, natural_payload=natural_payload)
    return {
        "route_confidence": 98 if exact else (active_action_language.confidence if active_action_language else 96),
        "confidence_reason": "active_task_exact_action_alias" if exact else (active_action_language.reason if active_action_language else "active_task_action_language"),
        "tool_candidates": [task.tool] if task and getattr(task, "tool", None) else [],
        "fallback_used": False,
        "requires_clarification": False,
        "active_task_action_language": diagnostic,
    }


class MainRouter:
    def __init__(self, kernel: StateKernel | None = None):
        self.kernel = kernel or StateKernel()

    def route(self, req: ChatRequest) -> ChatResponse:
        # Step 1/2: Load/create state first. Duplicate guard checks within conversation ledger.
        state = self.kernel.conversations.get_or_create(req.conversation_id, mode=req.mode)
        duplicate = self.kernel.events.find_by_client_event_id(state.conversation_id, req.client_event_id)
        if duplicate:
            cached = duplicate.get("response", {})
            return ChatResponse.model_validate({**cached, "duplicate": True})

        task = self.kernel.tasks.get(state.active_task_id)
        has_attachments = bool(req.attachments)
        intent = classify_intent(req.text, has_attachments=has_attachments)
        route_context = build_route_context(
            req.text,
            has_active_task=bool(task),
            has_pending_clarification=bool(task.pending_clarification) if task else False,
            has_attachments=has_attachments,
        )
        exact_action = route_context.exact_action
        active_action_language = route_context.active_action_language
        action = route_context.action
        qs_alias = route_context.qs_alias
        tool_ambiguity = route_context.tool_ambiguity
        negative_guard = route_context.negative_guard
        confidence_shadow = score_route_candidates(
            req.text,
            has_active_task=bool(task),
            active_tool=getattr(task, "tool", None) if task else None,
            has_pending_clarification=bool(task.pending_clarification) if task else False,
            has_attachments=has_attachments,
        )

        def finalize(*args, **kwargs):
            kwargs.setdefault("route_context", route_context)
            return self._finalize(*args, **kwargs)

        # Step 3: Pending clarification gate. Workbook-read policy review is read-only and may be shown while pending.

        if task and task.pending_clarification:
            policy_decision = detect_workbook_read_policy_review(req.text)
            if policy_decision.matched:
                policy = evaluate_workbook_read_policy_review(
                    conversation_id=state.conversation_id,
                    client_event_id=req.client_event_id,
                )
                policy_meta = {
                    key: value
                    for key, value in policy.items()
                    if key not in {"conversation_id", "client_event_id", "route", "message", "readiness"}
                }
                policy_meta.update({
                    "route_confidence": policy_decision.confidence,
                    "confidence_reason": f"pending_clarification_policy_review:{policy_decision.reason}",
                    "tool_candidates": list(policy_decision.tool_candidates or ("builder",)),
                    "fallback_used": False,
                    "requires_clarification": False,
                    "plan_mutated": False,
                    "pending_clarification_preserved": True,
                })
                self.kernel.tasks.save(task)
                self.kernel.conversations.save(state)
                return finalize(
                    req,
                    state,
                    task,
                    policy_decision.intent,
                    "builder_workbook_read_policy_review",
                    policy["message"],
                    blocked=False,
                    reason="pending_clarification_read_only_policy_review_allowed",
                    router_step="pending_clarification_policy_review",
                    reducer_result={
                        "language_gate": policy_decision.as_dict(),
                        "plan_mutated": False,
                        "pending_clarification_preserved": True,
                        "pending_clarification_id": state.pending_clarification_id,
                    },
                    route_meta=policy_meta,
                    confidence_shadow=confidence_shadow,
                    confidence_control_taken=False,
                )

        # Review stays read-only and allowed while a clarification is open.
        if task and task.pending_clarification and action == "review":
            route, message, blocked, reason = self._handle_active_action(action, task, state)
            self.kernel.tasks.save(task)
            self.kernel.conversations.save(state)
            action_step = "active_task_action" if exact_action else "active_task_action_language_gate"
            route_meta = _active_action_route_meta(action, route, task, exact=bool(exact_action), active_action_language=active_action_language)
            return finalize(req, state, task, intent, route, message, blocked=blocked, reason=reason, router_step=action_step, route_meta=route_meta)

        if task and task.pending_clarification:
            route, message, closed, blocked, reason, pending_reducer_result = handle_pending_clarification(task, req.text)
            if closed:
                state.pending_clarification_id = None
            if route == "active_task_start_new":
                state.active_task_id = None
                state.active_workbook_id = None
            elif route == "active_task_cancelled":
                state.active_task_id = None
                state.active_workbook_id = None
            self.kernel.tasks.save(task)
            self.kernel.conversations.save(state)
            intent_for_response = "CLARIFICATION_ANSWER" if route == "clarification_resolved" else intent
            snapshot_ctx = self._mark_snapshot_stale_if_plan_changed(state, task, pending_reducer_result if isinstance(pending_reducer_result, dict) else None)
            if snapshot_ctx and snapshot_ctx.get("status") == "stale" and pending_reducer_result and (pending_reducer_result.get("changed_slots") or []):
                message = f"{message} The existing Builder snapshot is now stale because the plan changed."
            return finalize(req, state, task, intent_for_response, route, message, blocked=blocked, reason=reason, router_step="pending_clarification_gate", reducer_result=pending_reducer_result, snapshot=snapshot_ctx)

        # Step 4: Attachment bind. Alpha.6 binds metadata only; no workbook reading.
        if has_attachments and task and task.tool == "builder" and task.status != "cancelled":
            attachment = self.kernel.attachments.register_meta(req.attachments[0], bound_to_task_id=task.task_id)
            task.workbook = attachment
            task.status = "collecting"
            state.active_workbook_id = attachment["workbook_id"]
            snapshot_ctx = self._mark_active_snapshot_stale_for_workbook_change(state, task)
            self.kernel.tasks.save(task)
            self.kernel.conversations.save(state)
            return finalize(
                req,
                state,
                task,
                intent,
                "attachment_bind",
                "Workbook received. I kept it bound to the active Builder task.",
                reason="active_builder_attachment_bound_metadata_only",
                router_step="attachment_bind",
                reducer_result={"workbook": public_workbook_ref(attachment), "workbook_read": False},
                snapshot=snapshot_ctx,
            )

        if has_attachments and not task:
            attachment = self.kernel.attachments.register_meta(req.attachments[0])
            return finalize(
                req,
                state,
                None,
                intent,
                "attachment_received_no_active_task",
                "Workbook received. Tell me what you want to do with it.",
                reason="attachment_present_no_active_task",
                router_step="attachment_bind",
                reducer_result={"workbook": public_workbook_ref(attachment), "workbook_read": False},
            )

        # Step 5A: Active task issue feedback must be read-only and must win
        # before action language. Phrases like "Preview is broken" mention
        # preview but are reports, not preview commands.
        if task and is_active_task_issue_feedback(req.text):
            message = handle_feedback(task, req.text)
            self.kernel.tasks.save(task)
            return finalize(req, state, task, intent, "feedback_read_only", message, reason="feedback_logged_no_plan_mutation", router_step="feedback_router")

        # Step 5B: Active-task direct workbook-content read / bypass commands
        # must be blocked before active action routing. Phrases like "run preview"
        # can otherwise be interpreted as normal active actions even when the
        # same text explicitly asks to read cells, formulas, raw paths, parse a
        # workbook, or bypass no-engine locks.
        if task and req.text.strip() and detect_active_task_content_read_attack(req.text):
            return finalize(
                req,
                state,
                task,
                "ACTIVE_TASK_CONTENT_READ_BLOCKED",
                "clarification_blocked_action",
                "Workbook content reading is blocked in this stage. I kept the active Builder task unchanged. Cells, formulas, dimensions, raw paths, workbook parsing, legacy Builder, and engine execution remain disabled.",
                blocked=True,
                reason="active_task_content_read_blocked_by_policy",
                router_step="active_task_content_read_safe_block",
                reducer_result={"plan_mutated": False},
                route_meta={
                    "route_confidence": 99,
                    "confidence_reason": "active_task_content_read_blocked_by_policy",
                    "tool_candidates": [task.tool] if getattr(task, "tool", None) else ["builder"],
                    "fallback_used": False,
                    "requires_clarification": False,
                    "plan_mutated": False,
                    "workbook_opened": False,
                    "workbook_read": False,
                    "workbook_content_read": False,
                    "workbook_parsed": False,
                    "cells_read": False,
                    "formulas_read": False,
                    "engine_called": False,
                    "excel_created": False,
                    "contract_only": True,
                    "legacy_builder_called": False,
                    "preview_readiness_upgraded": False,
                    "export_readiness_upgraded": False,
                    "safety": {
                        "workbook_opened": False,
                        "workbook_read": False,
                        "workbook_content_read": False,
                        "workbook_parsed": False,
                        "cells_read": False,
                        "formulas_read": False,
                        "engine_called": False,
                        "excel_created": False,
                        "contract_only": True,
                        "legacy_builder_called": False,
                        "preview_readiness_upgraded": False,
                        "export_readiness_upgraded": False,
                    },
                },
            )

        # Step 5: Active task action.
        if task and action:
            route, message, blocked, reason = self._handle_active_action(action, task, state)
            self.kernel.tasks.save(task)
            self.kernel.conversations.save(state)
            action_step = "active_task_action" if exact_action else "active_task_action_language_gate"
            route_meta = _active_action_route_meta(action, route, task, exact=bool(exact_action), active_action_language=active_action_language)
            return finalize(req, state, task, intent, route, message, blocked=blocked, reason=reason, router_step=action_step, route_meta=route_meta)

        # Step 6: Feedback/correction. Alpha.22.2D keeps no-active-task
        # wording cleanup under NoActiveTaskLanguageGate; feedback routing owns
        # active-task issue reports or explicit standalone feedback only.
        if (task and is_active_task_issue_feedback(req.text)) or (intent == "FEEDBACK" and is_explicit_standalone_feedback(req.text)):
            message = handle_feedback(task, req.text)
            if task:
                self.kernel.tasks.save(task)
            return finalize(req, state, task, intent, "feedback_read_only", message, reason="feedback_logged_no_plan_mutation", router_step="feedback_router")

        # Step 7 removed in alpha.22.2C: no-active-task writing/casual/tool/soft Builder
        # language is now owned by NoActiveTaskLanguageGate after protected contexts.

        # Step 7E: Active task non-mutating language gate. This prevents normal
        # greetings, writing help, casual help, CostX/QS explanations, and other
        # non-mutating text from falling into the setup slot reducer. Setup edits
        # remain owned by slot_reducer only.
        if task and req.text.strip():
            active_language = is_active_task_non_mutating_language(req.text)
            if active_language.matched and not is_explicit_setup_command_text(req.text):
                payload = active_language.as_dict()
                return finalize(
                    req,
                    state,
                    task,
                    active_language.intent,
                    active_language.route,
                    "I kept the active Builder setup unchanged. I can help with that without changing the plan.",
                    blocked=False,
                    reason=active_language.reason,
                    router_step="active_task_non_mutating_language_gate",
                    route_meta={
                        "route_confidence": active_language.confidence,
                        "confidence_reason": active_language.reason,
                        "tool_candidates": list(active_language.tool_candidates or (task.tool,)),
                        "fallback_used": False,
                        "requires_clarification": False,
                        "non_mutating_category": active_language.category,
                        "active_task_language": payload,
                        "plan_mutated": False,
                    },
                )

        # Step 8: Active task no-fallback guards. Do not let new-command aliases or
        # ambiguous short phrases reset or escape the active tool context.
        if task and intent == "NEW_COMMAND" and req.text.strip() and not is_explicit_new_task_request(req.text) and not looks_like_slot_edit_text(task.plan, req.text):
            alias_detail = qs_alias.as_dict() if qs_alias.matched else {}
            return finalize(
                req,
                state,
                task,
                "ACTIVE_TASK_NEW_COMMAND_AMBIGUOUS",
                "active_task_new_command_confirmation",
                "I see a new QS/Builder-style command, but there is already an active task. Reply 'start new' to discard the current task, or use Review to keep working on it.",
                blocked=False,
                reason="active_task_priority_preserved",
                router_step="active_task_new_command_guard",
                reducer_result={"qs_alias": alias_detail, "plan_mutated": False},
                route_meta={
                    "route_confidence": 98,
                    "confidence_reason": f"active_task_present + qs_alias:{alias_detail.get('alias', 'new_command')}",
                    "tool_candidates": ["builder"],
                    "fallback_used": False,
                    "requires_clarification": True,
                },
            )

        if task and intent == "GENERAL" and tool_ambiguity.matched and req.text.strip():
            candidates = list(tool_ambiguity.tool_candidates or ("builder",))
            if "formatter" in candidates:
                route = "formatter_handoff_needs_confirmation"
                message = "I read this as a possible Formatter action, but no Formatter execution is connected in this alpha. Confirm whether you want to hand off the latest Builder output to Formatter later, or use Review to stay in Builder."
            else:
                route = "active_task_slot_edit_needs_clarification"
                message = "I kept the active task unchanged. Please clarify what you want to change or choose Review, Preview, Export, Cancel, or Start new."
            return finalize(
                req,
                state,
                task,
                "ACTIVE_TASK_AMBIGUOUS_TOOL_PHRASE",
                route,
                message,
                blocked=False,
                reason="ambiguous_tool_phrase_needs_clarification",
                router_step="no_fallback_clarification_guard",
                reducer_result={"ambiguity": tool_ambiguity.as_dict(), "plan_mutated": False},
                route_meta={
                    "route_confidence": 98,
                    "confidence_reason": f"active_task_present + ambiguous_tool_phrase:{tool_ambiguity.alias}",
                    "tool_candidates": candidates,
                    "fallback_used": False,
                    "requires_clarification": True,
                },
            )

        # Step 8: Active task slot reducer. Alpha.3 applies narrow typed plan edits only.
        if task and req.text.strip() and looks_like_slot_edit_text(task.plan, req.text):
            task.plan, reducer_result = apply_slot_edit(task.plan, req.text)
            if reducer_result.handled:
                if reducer_result.requires_clarification and reducer_result.clarification:
                    clarification = reducer_result.clarification
                    clarification["task_id"] = task.task_id
                    task.pending_clarification = clarification
                    task.status = "needs_clarification"
                    state.pending_clarification_id = clarification["clarification_id"]
                    self.kernel.tasks.save(task)
                    self.kernel.conversations.save(state)
                    reducer_payload = reducer_result.model_dump(mode="json")
                    snapshot_ctx = self._snapshot_context(state, task)
                    return finalize(
                        req, state, task, "SLOT_EDIT", "active_task_slot_edit_needs_clarification", reducer_result.message,
                        blocked=False, reason="slot_reducer_requires_clarification", router_step="slot_reducer", reducer_result=reducer_payload, snapshot=snapshot_ctx
                    )
                self.kernel.tasks.save(task)
                self.kernel.conversations.save(state)
                reducer_payload = reducer_result.model_dump(mode="json")
                snapshot_ctx = self._mark_snapshot_stale_if_plan_changed(state, task, reducer_payload)
                message = reducer_result.message
                if snapshot_ctx and snapshot_ctx.get("status") == "stale" and (reducer_payload.get("changed_slots") or []):
                    message = f"{message} The existing Builder snapshot is now stale because the plan changed."
                return finalize(
                    req, state, task, "SLOT_EDIT", "active_task_slot_edit", message,
                    blocked=False, reason="slot_reducer_applied", router_step="slot_reducer", reducer_result=reducer_payload, snapshot=snapshot_ctx
                )
            self.kernel.tasks.save(task)
            return finalize(
                req,
                state,
                task,
                "SLOT_EDIT",
                "active_task_edit_unhandled",
                reducer_result.message,
                blocked=True,
                reason="slot_reducer_unhandled",
                router_step="slot_reducer",
                reducer_result=reducer_result.model_dump(mode="json"),
            )

        # Step 9: Active task safe fallback. Active Builder context must never
        # leak to the no-active/general fallback layer. This route is read-only,
        # asks for clarification, and does not mutate the plan.
        if task and req.text.strip():
            return finalize(
                req,
                state,
                task,
                "ACTIVE_TASK_CONTEXT_UNHANDLED",
                "active_task_context_unhandled",
                "I kept the active task unchanged. Please clarify the Builder action or use Review, Preview, Export, Download, Cancel, or Start new.",
                blocked=False,
                reason="active_task_context_unhandled_no_mutation",
                router_step="active_task_context_guard",
                reducer_result={"plan_mutated": False},
                route_meta={
                    "route_confidence": 88,
                    "confidence_reason": "active_task_present_no_route_owner",
                    "tool_candidates": [task.tool],
                    "fallback_used": False,
                    "requires_clarification": True,
                    "plan_mutated": False,
                },
            )

        # Step 10: No-active exact action guard. Preview/export/download/review
        # aliases need an active Builder task, so do not let them fall to the
        # general fallback when no task exists. This guard is read-only and
        # does not create or execute anything.
        if not task and action:
            return self._no_active_action_needs_active_task_response(req, state, action, confidence_shadow, route_context)

        # Step 11: No-active-task language gate. This is the single owner for
        # writing help, casual non-tool guards, generic choose-tool ambiguity,
        # and soft/exact Builder shell starts when no protected context exists.
        if not task:
            no_active_language = self._no_active_task_language_gate_response(req, state, intent, confidence_shadow, route_context)
            if no_active_language is not None:
                return no_active_language

        # Step 11: General fallback stub only.
        return finalize(
            req, state, task, intent, "general_stub", f"{APP_VERSION} is online. No active tool action was taken.",
            reason="no_active_task_or_command",
            router_step="general_stub",
            route_meta={
                "route_confidence": 85,
                "confidence_reason": "no_tool_signal_detected",
                "tool_candidates": [],
                "fallback_used": True,
                "requires_clarification": False,
            },
        )

    def _create_builder_shell_from_decision(
        self,
        req: ChatRequest,
        state,
        decision: NoActiveTaskLanguageDecision,
    ):
        """Single owner for creating a Builder shell from router decisions."""
        task = self.kernel.tasks.create(
            conversation_id=state.conversation_id,
            tool="builder",
            status="waiting_for_file",
            plan=default_builder_shell_plan(req.text),
        )
        state.active_task_id = task.task_id
        self.kernel.conversations.save(state)
        return task

    def _decision_route_meta(self, decision: NoActiveTaskLanguageDecision, *, confidence_shadow: dict[str, Any]) -> dict[str, Any]:
        confidence_reason = decision.reason or confidence_shadow.get("confidence_reason") or decision.route
        return {
            "route_confidence": int(decision.confidence or confidence_shadow.get("would_confidence") or 90),
            "confidence_reason": confidence_reason,
            "tool_candidates": list(decision.tool_candidates or []),
            "fallback_used": False,
            "requires_clarification": bool(decision.requires_clarification),
        }

    def _language_gate_control_allowed(self, decision: NoActiveTaskLanguageDecision, confidence_shadow: dict[str, Any]) -> bool:
        current_route = "choose_tool" if decision.route == "choose_tool" else "general_stub"
        return confidence_engine_can_control(
            has_active_task=False,
            has_pending_clarification=False,
            has_attachments=False,
            current_route=current_route,
            score=confidence_shadow,
        )

    def _no_active_action_needs_active_task_response(
        self,
        req: ChatRequest,
        state,
        action: str,
        confidence_shadow: dict[str, Any],
        route_context: RouteContext | None = None,
    ) -> ChatResponse:
        route_meta = {
            "route_confidence": 98,
            "confidence_reason": "no_active_action_requires_active_task",
            "tool_candidates": ["builder"],
            "fallback_used": False,
            "requires_clarification": True,
            "blocked": False,
            "plan_mutated": False,
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "legacy_builder_called": False,
            "active_task_action_language": _active_action_diagnostic_payload(
                action,
                "no_active_action_needs_active_task",
                exact=bool(route_context.exact_action) if route_context else True,
                natural_payload=(route_context.active_action_language.as_dict() if route_context and route_context.active_action_language else None),
            ),
        }
        action_label = (action or "action").replace("_", " ")
        return self._finalize(
            req,
            state,
            None,
            "NO_ACTIVE_ACTION_NEEDS_ACTIVE_TASK",
            "no_active_action_needs_active_task",
            f"There is no active Builder task to {action_label}. Start or restore a Builder setup first.",
            blocked=False,
            reason="no_active_action_requires_active_task",
            router_step="no_active_action_guard",
            reducer_result={"plan_mutated": False, "action": action},
            route_meta=route_meta,
            route_context=route_context,
            confidence_shadow=confidence_shadow,
            confidence_control_taken=False,
        )

    def _no_active_task_language_gate_response(
        self,
        req: ChatRequest,
        state,
        intent: str,
        confidence_shadow: dict[str, Any],
        route_context: RouteContext | None = None,
    ) -> ChatResponse | None:
        if req.attachments:
            return None
        decision = route_context.no_active_language if route_context and route_context.no_active_language is not None else classify_no_active_task_language(req.text)
        if not decision.matched:
            return None
        control_taken = self._language_gate_control_allowed(decision, confidence_shadow)
        route_meta = self._decision_route_meta(decision, confidence_shadow=confidence_shadow)

        if decision.route == "new_builder_task_shell":
            task = self._create_builder_shell_from_decision(req, state, decision)
            qs_alias = {
                "matched": True,
                "alias": decision.alias,
                "canonical_intent": "builder_start",
                "confidence": decision.confidence,
                "region_hint": decision.region_hint,
                "requires_setup": True,
                "negative_guard": None,
                "tool_candidates": list(decision.tool_candidates or ("builder",)),
            }
            return self._finalize(
                req,
                state,
                task,
                "NEW_COMMAND",
                "new_builder_task_shell",
                "I can start a Builder task. Please attach the workbook and confirm trade/profile, function, unit, zones/headings, and levels.",
                blocked=False,
                reason=decision.reason,
                router_step="no_active_task_language_gate",
                reducer_result={"qs_alias": qs_alias, "confidence_engine": {"would_route": "new_builder_task_shell", "plan_mutated": False}},
                route_meta=route_meta,
                route_context=route_context,
                confidence_shadow=confidence_shadow,
                confidence_control_taken=control_taken,
            )

        if decision.route == "builder_workbook_read_policy_review":
            policy = evaluate_workbook_read_policy_review(
                conversation_id=state.conversation_id,
                client_event_id=req.client_event_id,
            )
            policy_meta = {
                key: value
                for key, value in policy.items()
                if key not in {"conversation_id", "client_event_id", "route", "message"}
            }
            route_meta = {
                **route_meta,
                **policy_meta,
                "fallback_used": False,
                "requires_clarification": False,
                "tool_candidates": list(decision.tool_candidates or ("builder",)),
                "plan_mutated": False,
            }
            return self._finalize(
                req,
                state,
                None,
                decision.intent,
                "builder_workbook_read_policy_review",
                policy["message"],
                blocked=False,
                reason=decision.reason,
                router_step="no_active_task_language_gate",
                reducer_result={"language_gate": decision.as_dict(), "plan_mutated": False},
                route_meta=route_meta,
                route_context=route_context,
                confidence_shadow=confidence_shadow,
                confidence_control_taken=control_taken,
            )

        if decision.route == "registry_advisory_metadata_only":
            advisory = requirement_check(req.text)
            route_meta = {
                **route_meta,
                "metadata_only": True,
                "execution_enabled": False,
                "workbook_read": False,
                "engine_called": False,
                "excel_created": False,
                "legacy_builder_called": False,
                "safety": {
                    "metadata_only": True,
                    "execution_enabled": False,
                    "workbook_read": False,
                    "engine_called": False,
                    "excel_created": False,
                    "legacy_builder_called": False,
                },
                "requirement_advisor": advisory,
                "registry_advisory": {"matched": True, "decision": decision.as_dict(), "requirement_advisor": advisory},
                "tool_candidates": advisory.get("tool_candidates") or list(decision.tool_candidates or []),
                "requires_clarification": True,
            }
            return self._finalize(
                req,
                state,
                None,
                decision.intent,
                "registry_advisory_metadata_only",
                "This is a registry advisory request only. I can show capability/tool metadata and requirements, but no tool execution is enabled in this alpha.",
                blocked=False,
                reason=decision.reason,
                router_step="registry_advisory_language_gate",
                reducer_result={"language_gate": decision.as_dict(), "plan_mutated": False},
                route_meta=route_meta,
                route_context=route_context,
                confidence_shadow=confidence_shadow,
                confidence_control_taken=control_taken,
            )

        if decision.route == "no_active_prompt_injection_safe_block":
            route_meta = {
                **route_meta,
                "metadata_only": True,
                "execution_enabled": False,
                "workbook_read": False,
                "workbook_content_read": False,
                "workbook_opened": False,
                "workbook_parsed": False,
                "cells_read": False,
                "formulas_read": False,
                "engine_called": False,
                "excel_created": False,
                "legacy_builder_called": False,
                "preview_readiness_upgraded": False,
                "export_readiness_upgraded": False,
                "plan_mutated": False,
                "safety": {
                    "metadata_only": True,
                    "execution_enabled": False,
                    "workbook_read": False,
                    "workbook_content_read": False,
                    "workbook_opened": False,
                    "workbook_parsed": False,
                    "cells_read": False,
                    "formulas_read": False,
                    "engine_called": False,
                    "excel_created": False,
                    "legacy_builder_called": False,
                    "preview_readiness_upgraded": False,
                    "export_readiness_upgraded": False,
                },
                "requires_clarification": False,
                "tool_candidates": [],
                "fallback_used": False,
            }
            return self._finalize(
                req,
                state,
                None,
                decision.intent,
                "no_active_prompt_injection_safe_block",
                "I blocked this as unsafe instruction-like text. No Jarvis tool, workbook, engine, or file action was run.",
                blocked=True,
                reason="no_active_prompt_injection_safe_block",
                router_step="no_active_task_language_gate",
                reducer_result={"language_gate": decision.as_dict(), "plan_mutated": False},
                route_meta=route_meta,
                route_context=route_context,
                confidence_shadow=confidence_shadow,
                confidence_control_taken=control_taken,
            )

        if decision.route == "choose_tool":
            return self._finalize(
                req,
                state,
                None,
                decision.intent,
                "choose_tool",
                "That could relate to a Jarvis tool. Please choose Builder, Formatter, QA Checker, or ask a general question.",
                blocked=False,
                reason="no_active_task_language_gate_choose_tool",
                router_step="no_active_task_language_gate",
                reducer_result={"language_gate": decision.as_dict(), "plan_mutated": False},
                route_meta=route_meta,
                route_context=route_context,
                confidence_shadow=confidence_shadow,
                confidence_control_taken=control_taken,
            )

        if decision.route == "general_stub":
            message = f"{APP_VERSION} is online. No active tool action was taken."
            if decision.category == "writing_help":
                message = "I can help clean up or rewrite the wording here. Paste the sentence, reply, note, or paragraph you want polished."
            elif decision.category == "casual_non_tool":
                message = f"{APP_VERSION} is online. I treated this as a general question, not a Jarvis tool action."
            return self._finalize(
                req,
                state,
                None,
                decision.intent,
                "general_stub",
                message,
                blocked=False,
                reason=decision.public_negative_guard or decision.reason,
                router_step="no_active_task_language_gate",
                reducer_result={"language_gate": decision.as_dict(), "plan_mutated": False},
                route_meta=route_meta,
                route_context=route_context,
                confidence_shadow=confidence_shadow,
                confidence_control_taken=control_taken,
            )

        return None

    def _snapshot_context(self, state, task) -> dict[str, Any] | None:
        snapshot = self.kernel.snapshots.get_active(state.conversation_id)
        if not snapshot:
            return None
        active_plan_hash = plan_hash_from_plan(task.plan if task else {})
        # Defensive freshness check: if a current snapshot no longer matches the active plan,
        # mark it stale even if the reducer invalidation path was bypassed.
        if snapshot.status == "current" and snapshot.source_plan_hash and snapshot.source_plan_hash != active_plan_hash:
            snapshot = self.kernel.snapshots.mark_active_stale(
                state.conversation_id,
                reason="active_plan_changed_after_snapshot",
                active_plan_hash=active_plan_hash,
            ) or snapshot
        if snapshot.status == "stale":
            self._mark_adapter_stale_for_snapshot(state.conversation_id, snapshot.snapshot_id)
        return {
            "snapshot_id": snapshot.snapshot_id,
            "status": snapshot.status,
            "stale_reason": snapshot.stale_reason,
            "source_plan_hash": snapshot.source_plan_hash,
            "active_plan_hash": active_plan_hash,
            "snapshot_hash": snapshot.snapshot_hash,
            "workbook_ref": public_workbook_ref(snapshot.workbook_ref),
        }

    def _mark_snapshot_stale_if_plan_changed(self, state, task, reducer_result: dict[str, Any] | None) -> dict[str, Any] | None:
        if not reducer_result:
            return self._snapshot_context(state, task)
        changed_slots = reducer_result.get("changed_slots") or []
        if not changed_slots:
            return self._snapshot_context(state, task)
        active_plan_hash = plan_hash_from_plan(task.plan if task else {})
        snapshot = self.kernel.snapshots.mark_active_stale(
            state.conversation_id,
            reason="active_plan_changed_after_snapshot",
            active_plan_hash=active_plan_hash,
        )
        if snapshot and snapshot.status == "stale":
            self._mark_adapter_stale_for_snapshot(state.conversation_id, snapshot.snapshot_id)
            return {
                "snapshot_id": snapshot.snapshot_id,
                "status": snapshot.status,
                "stale_reason": snapshot.stale_reason,
                "source_plan_hash": snapshot.source_plan_hash,
                "active_plan_hash": active_plan_hash,
                "snapshot_hash": snapshot.snapshot_hash,
                "workbook_ref": public_workbook_ref(snapshot.workbook_ref),
            }
        return self._snapshot_context(state, task)

    def _mark_active_snapshot_stale_for_workbook_change(self, state, task) -> dict[str, Any] | None:
        snapshot = self.kernel.snapshots.get_active(state.conversation_id)
        if not snapshot:
            return None
        active_plan_hash = plan_hash_from_plan(task.plan if task else {})
        snapshot = self.kernel.snapshots.mark_active_stale(
            state.conversation_id,
            reason="workbook_ref_changed_after_snapshot",
            active_plan_hash=active_plan_hash,
        ) or snapshot
        if snapshot.status == "stale":
            self._mark_adapter_stale_for_snapshot(state.conversation_id, snapshot.snapshot_id)
        return {
            "snapshot_id": snapshot.snapshot_id,
            "status": snapshot.status,
            "stale_reason": snapshot.stale_reason,
            "source_plan_hash": snapshot.source_plan_hash,
            "active_plan_hash": active_plan_hash,
            "snapshot_hash": snapshot.snapshot_hash,
            "workbook_ref": public_workbook_ref(snapshot.workbook_ref),
        }

    def _mark_adapter_stale_for_snapshot(self, conversation_id: str, snapshot_id: str | None) -> None:
        if not snapshot_id:
            return
        updated = self.kernel.adapters.mark_snapshot_stale(snapshot_id, reason="source_snapshot_is_stale")
        if not updated:
            return
        state = self.kernel.conversations.get(conversation_id)
        task = self.kernel.tasks.get(state.active_task_id) if state else None
        if task:
            latest = self.kernel.adapters.get_latest(conversation_id)
            if latest and latest.snapshot_id == snapshot_id:
                task.adapter_dry_run_result = latest.model_dump(mode="json")
                self.kernel.tasks.save(task)

    def _adapter_context(self, state, snapshot_ctx: dict[str, Any] | None = None) -> dict[str, Any] | None:
        latest_adapter = self.kernel.adapters.get_latest(state.conversation_id)
        if not latest_adapter:
            return None
        if snapshot_ctx and snapshot_ctx.get("status") == "stale" and latest_adapter.snapshot_id == snapshot_ctx.get("snapshot_id"):
            self._mark_adapter_stale_for_snapshot(state.conversation_id, latest_adapter.snapshot_id)
            latest_adapter = self.kernel.adapters.get_latest(state.conversation_id) or latest_adapter
        payload = adapter_trace_payload(latest_adapter) or {}
        return {
            "adapter_input_id": latest_adapter.adapter_input_id,
            "snapshot_id": latest_adapter.snapshot_id,
            "snapshot_status": payload.get("snapshot_status"),
            "freshness": payload.get("freshness", "current"),
            "stale_reason": payload.get("stale_reason"),
            "engine_called": latest_adapter.engine_called,
            "excel_created": latest_adapter.excel_created,
            "workbook_read": getattr(latest_adapter, "workbook_read", False),
            "valid_for_dry_run": bool(payload.get("valid_for_dry_run", latest_adapter.validation.valid_for_dry_run)),
            "valid_for_future_engine": bool(payload.get("valid_for_future_engine", latest_adapter.validation.valid_for_future_engine)),
            "adapter_status": payload.get("adapter_status") or latest_adapter.adapter_status,
            "setup_completeness": payload.get("setup_completeness"),
            "normalization": payload.get("normalization"),
            "conflicts": payload.get("conflicts") or [],
        }

    def _engine_contract_context(self, state) -> dict[str, Any] | None:
        latest_contract = self.kernel.contracts.get_latest(state.conversation_id)
        if not latest_contract:
            return None
        payload = contract_trace_payload(latest_contract) or {}
        payload["engine_boundary_audit"] = boundary_audit_summary(latest_contract)
        return payload

    def _engine_preflight_context(self, state) -> dict[str, Any]:
        return preflight_summary(self.kernel.preflights.get_latest(state.conversation_id))

    def _engine_execution_context(self, state) -> dict[str, Any]:
        return execution_summary(self.kernel.executions.get_latest(state.conversation_id))

    def _workbook_read_policy_context(self, state) -> dict[str, Any]:
        """Return latest workbook-read policy visibility from event ledger.

        This is additive/read-only. It does not mutate Builder state, change
        routing, open workbooks, or upgrade preview/export readiness.
        """
        if not state:
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
        for event in reversed(self.kernel.events.list_events(state.conversation_id)):
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

    def _readiness_context(self, state, task, snapshot_ctx: dict[str, Any] | None = None, adapter_ctx: dict[str, Any] | None = None, setup: dict[str, Any] | None = None) -> dict[str, Any]:
        snapshot_ctx = snapshot_ctx if snapshot_ctx is not None else self._snapshot_context(state, task)
        adapter_ctx = adapter_ctx if adapter_ctx is not None else self._adapter_context(state, snapshot_ctx)
        contract_ctx = self._engine_contract_context(state)
        setup = setup or setup_completeness_from_plan(
            plan=task.plan if task else {},
            workbook_ref=task.workbook if task else None,
            pending_clarification=bool(task.pending_clarification) if task else False,
            snapshot_status=(snapshot_ctx or {}).get("status") if snapshot_ctx else None,
            adapter_freshness=(adapter_ctx or {}).get("freshness") if adapter_ctx else None,
        )
        normalization = plan_normalization_report(task.plan if task else {})
        return build_readiness_contract(
            task=task,
            state=state,
            setup=setup,
            snapshot=snapshot_ctx or {},
            adapter=adapter_ctx or {},
            engine_contract=contract_ctx or {},
            engine_boundary_audit=(contract_ctx or {}).get("engine_boundary_audit") or {},
            normalization=normalization,
            conflicts=[],
            workbook_read_policy=self._workbook_read_policy_context(state),
        )

    def _handle_active_action(self, action: str, task, state) -> tuple[str, str, bool, str]:
        if action == "review":
            snapshot_ctx = self._snapshot_context(state, task)
            adapter_ctx = self._adapter_context(state, snapshot_ctx)
            contract_ctx = self._engine_contract_context(state)
            preflight_ctx = self._engine_preflight_context(state)
            execution_ctx = self._engine_execution_context(state)
            setup = setup_completeness_from_plan(
                plan=task.plan or {},
                workbook_ref=task.workbook,
                pending_clarification=bool(task.pending_clarification),
                snapshot_status=(snapshot_ctx or {}).get("status") if snapshot_ctx else None,
                adapter_freshness=(adapter_ctx or {}).get("freshness") if adapter_ctx else None,
            )
            normalization = plan_normalization_report(task.plan or {})
            readiness = build_readiness_contract(
                task=task,
                state=state,
                setup=setup,
                snapshot=snapshot_ctx or {},
                adapter=adapter_ctx or {},
                engine_contract=contract_ctx or {},
                engine_boundary_audit=(contract_ctx or {}).get("engine_boundary_audit") or {},
                normalization=normalization,
                conflicts=[],
                workbook_read_policy=self._workbook_read_policy_context(state),
            )
            workbook = {"found": bool(task.workbook), **(public_workbook_ref(task.workbook) or {})}
            message = build_review_message(
                plan_summary=plan_summary(task.plan or {}),
                workbook=workbook,
                setup=setup,
                readiness=readiness,
                normalization=normalization,
                snapshot={"found": bool(snapshot_ctx), **(snapshot_ctx or {})},
                adapter=adapter_ctx or {},
                engine_contract=contract_ctx or {},
                engine_preflight=preflight_ctx or {},
                engine_execution=execution_ctx or {},
            )
            return "active_task_review", message, False, "review_is_read_only"

        if action in {"preview", "approve_preview"}:
            snapshot_ctx = self._snapshot_context(state, task)
            setup = setup_completeness_from_plan(
                plan=task.plan or {},
                workbook_ref=task.workbook,
                pending_clarification=bool(task.pending_clarification),
                snapshot_status=(snapshot_ctx or {}).get("status") if snapshot_ctx else None,
            )
            missing = ", ".join(setup.get("missing_required") or []) or "none"
            if snapshot_ctx and snapshot_ctx.get("status") == "stale":
                return "active_task_preview_stub", f"Preview is not connected in {APP_VERSION}. The existing Builder snapshot is stale because the plan changed. Create a new snapshot before future preview/export integration. Future engine readiness: not ready. Missing: {missing}.", True, "preview_engine_not_connected"
            if snapshot_ctx and snapshot_ctx.get("status") == "current":
                return "active_task_preview_stub", f"Preview is not connected in {APP_VERSION}. A current Builder snapshot exists, but No Builder engine was called. Future engine readiness: {'ready' if setup.get('ready_for_future_engine') else 'not ready'}. Missing: {missing}.", True, "preview_engine_not_connected"
            return "active_task_preview_stub", f"Preview is not connected in {APP_VERSION}. No Builder engine was called. Future engine readiness: not ready. Missing: {missing}.", True, "preview_engine_not_connected"

        if action == "export":
            snapshot_ctx = self._snapshot_context(state, task)
            setup = setup_completeness_from_plan(
                plan=task.plan or {},
                workbook_ref=task.workbook,
                pending_clarification=bool(task.pending_clarification),
                snapshot_status=(snapshot_ctx or {}).get("status") if snapshot_ctx else None,
            )
            missing = ", ".join(setup.get("missing_required") or []) or "none"
            if snapshot_ctx and snapshot_ctx.get("status") == "stale":
                return "active_task_export_stub", f"Export is not connected in {APP_VERSION}. The existing Builder snapshot is stale because the plan changed. Create a new snapshot before future preview/export integration. Future engine readiness: not ready. Missing: {missing}.", True, "export_engine_not_connected"
            if snapshot_ctx and snapshot_ctx.get("status") == "current":
                return "active_task_export_stub", f"Export is not connected in {APP_VERSION}. A current Builder snapshot exists, but No Builder engine was called. Future engine readiness: {'ready' if setup.get('ready_for_future_engine') else 'not ready'}. Missing: {missing}.", True, "export_engine_not_connected"
            return "active_task_export_stub", f"Export is not connected in {APP_VERSION}. No Builder engine was called. Future engine readiness: not ready. Missing: {missing}.", True, "export_engine_not_connected"

        if action == "download":
            return "active_task_action_stub", f"Download/output retrieval is not connected in {APP_VERSION}. No file was opened, generated, or downloaded.", True, "download_output_not_connected"

        if action == "cancel":
            # Plain cancel with no pending clarification cancels the task safely.
            task.status = "cancelled"
            state.active_task_id = None
            state.active_workbook_id = None
            return "active_task_cancelled", "Current task cancelled safely.", False, "task_cancelled"

        if action == "cancel_task":
            task.status = "cancelled"
            state.active_task_id = None
            state.active_workbook_id = None
            return "active_task_cancelled", "Current task cancelled safely.", False, "task_cancelled"

        if action == "start_new":
            task.status = "cancelled"
            state.active_task_id = None
            state.active_workbook_id = None
            return "active_task_start_new", "Current task cancelled. You can start a new command.", False, "start_new_requested"

        return "active_task_action_stub", f"Action recognized, but not implemented in {APP_VERSION}.", True, "action_not_implemented"

    def _default_route_meta(self, route: str, reason: str | None, router_step: str | None, task) -> dict[str, Any]:
        if route in {"new_builder_task_shell", "active_task_review", "active_task_preview_stub", "active_task_export_stub", "attachment_bind", "general_chat"}:
            confidence = 98
        elif route in {"active_task_slot_edit", "clarification_resolved"}:
            confidence = 96
        elif route in {"active_task_slot_edit_needs_clarification", "active_task_edit_unhandled"}:
            confidence = 92
        elif route == "general_stub":
            confidence = 85
        else:
            confidence = 90
        return {
            "route_confidence": confidence,
            "confidence_reason": reason or router_step or route,
            "tool_candidates": [task.tool] if task and getattr(task, "tool", None) else [],
            "fallback_used": route == "general_stub" and reason == "no_active_task_or_command",
            "requires_clarification": "clarification" in route or route in {"choose_tool", "active_task_new_command_confirmation", "formatter_handoff_needs_confirmation"},
        }

    def _finalize(self, req: ChatRequest, state, task, intent: str, route: str, message: str, *, blocked: bool = False, reason: str | None = None, router_step: str | None = None, reducer_result: dict[str, Any] | None = None, snapshot: dict[str, Any] | None = None, route_meta: dict[str, Any] | None = None, confidence_shadow: dict[str, Any] | None = None, confidence_control_taken: bool = False, route_context: RouteContext | None = None) -> ChatResponse:
        route_meta = route_meta or self._default_route_meta(route, reason, router_step, task)
        if confidence_shadow is None:
            # Shadow scoring must describe the route decision input state, not
            # the post-route state. new_builder_task_shell creates a task before
            # _finalize(), so score that case as no-active-task input.
            shadow_has_active_task = False if route == "new_builder_task_shell" else bool(task)
            confidence_shadow = score_route_candidates(
                req.text,
                has_active_task=shadow_has_active_task,
                active_tool=getattr(task, "tool", None) if task and shadow_has_active_task else None,
                has_pending_clarification=(router_step == "pending_clarification_gate") or (bool(task.pending_clarification) if task and shadow_has_active_task else False),
                has_attachments=bool(req.attachments),
            )
        confidence_shadow = attach_actual_route(
            confidence_shadow,
            actual_route=route,
            control_taken=confidence_control_taken,
            mode="limited_control" if confidence_control_taken else None,
        )
        response_payload: dict[str, Any] = {
            "conversation_id": state.conversation_id,
            "event_id": "pending",
            "intent": intent,
            "route": route,
            "message": message,
            "active_task_id": task.task_id if task and state.active_task_id else state.active_task_id,
            "active_task_status": task.status if task and state.active_task_id else None,
            "pending_clarification_id": state.pending_clarification_id,
            "blocked": blocked,
            "reason": reason,
            "router_step": router_step,
            "duplicate": False,
            "state": state.model_dump(mode="json"),
            "reducer_result": reducer_result,
            "snapshot": snapshot if snapshot is not None else self._snapshot_context(state, task),
            "route_confidence": route_meta.get("route_confidence"),
            "confidence_reason": route_meta.get("confidence_reason"),
            "tool_candidates": route_meta.get("tool_candidates") or [],
            "fallback_used": bool(route_meta.get("fallback_used", False)),
            "requires_clarification": bool(route_meta.get("requires_clarification", False)),
            "confidence_engine": confidence_shadow,
        }
        if route_context is not None:
            response_payload["route_context"] = route_context.as_trace()
        # Alpha.23: route-to-capability diagnostics are additive metadata only.
        # They must not affect route selection, Builder slot reducer ownership,
        # snapshot/adapter/contract/preflight/execution, or any tool execution.
        for optional_key in (
            "non_mutating_category",
            "active_task_language",
            "plan_mutated",
            "negative_guard",
            "negative_guard_detail",
            "active_task_action_language",
            "metadata_only",
            "execution_enabled",
            "policy_only",
            "current_access_tier",
            "current_allowed_operations",
            "current_blocked_operations",
            "future_access_tiers",
            "required_future_approval_gates",
            "blocked_by_policy",
            "cell_read_enabled",
            "formula_read_enabled",
            "dimension_read_enabled",
            "workbook_parse_enabled",
            "workbook_opened",
            "workbook_read",
            "workbook_content_read",
            "workbook_parsed",
            "cells_read",
            "formulas_read",
            "engine_called",
            "excel_created",
            "contract_only",
            "legacy_builder_called",
            "preview_readiness_upgraded",
            "export_readiness_upgraded",
            "next_safe_action",
            "requirement_advisor",
            "registry_advisory",
            "safety",
        ):
            if optional_key in route_meta:
                response_payload[optional_key] = route_meta.get(optional_key)
        safe_registry_routes = {
            "choose_tool",
            "general_stub",
            "general_chat",
            "active_task_non_mutating_language",
            "registry_advisory_metadata_only",
        }
        if route in safe_registry_routes and router_step not in {"slot_reducer", "pending_clarification_gate", "attachment_bind", "active_task_action"}:
            registry_assist = route_capability_diagnostics(req.text)
            if registry_assist:
                response_payload["registry_assist"] = registry_assist
                response_payload["capability_candidates"] = registry_assist.get("capability_candidates") or []
                if registry_assist.get("tool_candidates") and not response_payload.get("tool_candidates"):
                    response_payload["tool_candidates"] = registry_assist.get("tool_candidates") or []
        if route == "clarification_resolved":
            response_payload["clarification_resolved"] = True
        response_payload["adapter"] = self._adapter_context(state, response_payload.get("snapshot")) if state else None
        response_payload["setup_completeness"] = setup_completeness_from_plan(
            plan=task.plan if task else {},
            workbook_ref=task.workbook if task else None,
            pending_clarification=bool(task.pending_clarification) if task else False,
            snapshot_status=(response_payload.get("snapshot") or {}).get("status") if response_payload.get("snapshot") else None,
            adapter_freshness=(response_payload.get("adapter") or {}).get("freshness") if response_payload.get("adapter") else None,
        ) if task else None
        response_payload["readiness"] = self._readiness_context(
            state,
            task,
            response_payload.get("snapshot"),
            response_payload.get("adapter"),
            response_payload.get("setup_completeness"),
        ) if task else None
        event = self.kernel.events.append(
            state.conversation_id,
            client_event_id=req.client_event_id,
            intent=intent,
            route=route,
            request=req.model_dump(mode="json"),
            response=response_payload,
        )
        response_payload["event_id"] = event["event_id"]
        # Update cached response with real event_id.
        events = self.kernel.events.list_events(state.conversation_id)
        events[-1]["response"] = response_payload
        from jarvis_v5.core.json_store import write_json
        from jarvis_v5.config import EVENTS_DIR
        write_json(EVENTS_DIR / f"{state.conversation_id}.json", events)
        return ChatResponse.model_validate(response_payload)
