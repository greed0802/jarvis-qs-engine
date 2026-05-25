from __future__ import annotations

import re

from jarvis_v5.router.action_aliases import get_action_alias, normalize_text
from jarvis_v5.router.active_task_action_language_gate import detect_active_task_action_language
from jarvis_v5.schemas.active_task_schema import ActiveTask
from jarvis_v5.reducers.slot_reducer import apply_slot_edit, resolve_zone_replace_confirmation
from jarvis_v5.reducers.level_reducer import set_levels
from jarvis_v5.parsers.conflict_guard import plan_normalization_report
from jarvis_v5.registry.trade_profile_registry import clean_trade_registry_payload
from jarvis_v5.schemas.reducer_schema import ReducerResult

RISKY_ACTIONS = {"preview", "approve_preview", "export", "download", "run_builder", "workbook_access"}


def _classify_test_choice(text: str) -> str | None:
    normalized = normalize_text(text)
    if normalized in {"a", "option a", "choose a"}:
        return "a"
    if normalized in {"b", "option b", "choose b"}:
        return "b"
    if normalized in {"cancel", "cancel clarification"}:
        return "cancel"
    return None


def _detect_pending_risky_action_text(text: str) -> str | None:
    """Detect execution/workbook-access phrases while clarification is pending.

    This gate is pending-only. It prevents unrelated workbook-access text from
    being consumed as an answer to a pending clarification. It does not enable
    workbook read/open/preflight and does not affect no-active-task routing.
    """
    normalized = normalize_text(text)
    run_builder_phrases = {
        "run builder",
        "run builder now",
        "run the builder",
        "execute builder",
        "execute the builder",
        "call builder engine",
        "run current builder",
        "run current task",
        "run this builder",
    }
    if normalized in run_builder_phrases:
        return "run_builder"

    # Keep explicit policy-review wording read-only. MainRouter owns the
    # allow-through path before this pending gate is called. This guard keeps
    # direct content/open/preflight requests from resolving clarifications.
    policy_review_patterns = (
        r"\b(?:review|explain|show|check|describe|read)\b.*\bworkbook\s+read\s+policy\b",
        r"\bworkbook\s+read\s+policy\b.*\b(?:review|explain|show|check|only|not\s+the\s+workbook)\b",
    )
    if any(re.search(pattern, normalized, flags=re.I) for pattern in policy_review_patterns):
        return None

    workbook_access_patterns = (
        r"\b(?:read|extract|get|show|scan|inspect)\b.*\b(?:cells?|formulas?|cached\s+values?|dimensions?|used\s+ranges?|comments?|tables?|styles?)\b",
        r"\b(?:open|parse|inspect|scan)\b.*\bworkbook\b",
        r"\blist\b.*\b(?:sheets?|worksheets?)\b",
        r"\brun\b.*\bworkbook\s+read\s+preflight\b",
        r"\bworkbook\s+read\s+preflight\b",
        r"\b(?:raw_path|saved_path|saved\s+path|raw\s+path)\b",
    )
    if any(re.search(pattern, normalized, flags=re.I) for pattern in workbook_access_patterns):
        return "workbook_access"
    return None



def _is_trade_profile_clarification_answer(normalized: str, pending: dict, registry: dict) -> bool:
    """Return true only for direct answers to a trade-profile clarification.

    Prevents unrelated policy/workbook-access text from resolving a pending
    trade clarification merely because the pending context has a canonical
    trade stored in registry metadata.
    """
    canonical = normalize_text(registry.get("canonical_trade") or "")
    options = [normalize_text(option) for option in pending.get("options") or []]
    if normalized in options:
        return True
    if canonical and normalized in {
        canonical,
        f"use {canonical}",
        f"confirm {canonical}",
        f"choose {canonical}",
        "yes",
        "confirm",
        "use it",
        "use this",
    }:
        return True
    if canonical and normalized.startswith(("use ", "choose ", "confirm ")) and canonical in normalized:
        return True
    if any(token in normalized for token in (
        "xgetcustom",
        "reinforcement weight",
        "bar reinforcement weight",
        "unit t",
        "unit kg",
    )):
        return True
    return False



def _resolve_parser_conflict(task: ActiveTask, pending: dict, text: str) -> tuple[str, str, bool, bool, str | None, dict | None] | None:
    normalized = normalize_text(text)
    context = pending.get("context") or {}
    conflict_type = pending.get("type")

    if normalized in {"cancel", "cancel clarification"}:
        pending["status"] = "cancelled"
        task.pending_clarification = None
        if task.status == "needs_clarification":
            task.status = "collecting"
        result = ReducerResult(
            handled=True, action="cancelled", slot="setup", message="Clarification cancelled. The active Builder plan was not changed.",
            changed_slots=[], confidence=0.9, plan_mutated=False, normalization=plan_normalization_report(task.plan),
        )
        return "clarification_cancelled", result.message, True, False, "clarification_cancelled", result.model_dump(mode="json")

    # Trade/function conflicts are resolved by applying the selected option text.
    if conflict_type != "trade_profile_requires_clarification":
        for option in pending.get("options") or []:
            if normalized == normalize_text(option) or (normalized.startswith("use ") and normalize_text(option).endswith(normalized.replace("use ", "", 1))):
                if normalize_text(option) == "cancel":
                    continue
                task.plan, reducer_result = apply_slot_edit(task.plan, option)
                if reducer_result.handled and not reducer_result.requires_clarification:
                    pending["status"] = "resolved"
                    task.pending_clarification = None
                    if task.status == "needs_clarification":
                        task.status = "collecting"
                    return "clarification_resolved", reducer_result.message, True, False, "clarification_answer_resolved", reducer_result.model_dump(mode="json")


    if conflict_type == "trade_profile_requires_clarification":
        registry = context.get("trade_registry") or {}
        canonical = registry.get("canonical_trade")
        if normalized in {"cancel", "cancel clarification"}:
            return None
        if not _is_trade_profile_clarification_answer(normalized, pending, registry):
            return None
        # Keep the clarification gate strict, but allow the user to answer with
        # function/custom quantity/unit details for the matched trade.
        task.plan = task.plan or {}
        changed_slots: list[str] = []
        if canonical:
            task.plan["trade_profile"] = canonical
            task.plan["trade_registry"] = clean_trade_registry_payload(registry)
            changed_slots.extend(["trade_profile"])
        # Manual narrow parse for registry clarification answers. This avoids
        # re-triggering the same high-risk trade clarification on phrases like
        # "Reinforcement Weight".
        if "xgetcustom" in normalized:
            task.plan["costx_function"] = "XGETCUSTOM"
            changed_slots.append("costx_function")
        if "reinforcement weight" in normalized:
            task.plan["custom_quantity"] = "Bar Reinforcement Weight" if "bar reinforcement weight" in normalized else "Reinforcement Weight"
            task.plan["costx_function"] = "XGETCUSTOM"
            changed_slots.extend(["custom_quantity", "costx_function"])
        if "unit t" in normalized or normalized.endswith(" t"):
            task.plan["unit"] = "t"
            changed_slots.append("unit")
        if "unit kg" in normalized or normalized.endswith(" kg"):
            task.plan["unit"] = "kg"
            changed_slots.append("unit")
        if changed_slots:
            pending["status"] = "resolved"
            task.pending_clarification = None
            if task.status == "needs_clarification":
                task.status = "collecting"
            changed_slots = sorted(set(changed_slots))
            result = ReducerResult(
                handled=True, action="set", slot="trade_profile_registry",
                changes={key: task.plan.get(key) for key in ["trade_profile", "costx_function", "custom_quantity", "unit", "trade_registry"] if task.plan.get(key) is not None},
                message="Done — resolved trade/profile clarification.",
                changed_slots=changed_slots, confidence=0.9, plan_mutated=True,
                normalization=plan_normalization_report(task.plan),
                trade_registry=clean_trade_registry_payload(registry),
            )
            return "clarification_resolved", result.message, True, False, "clarification_answer_resolved", result.model_dump(mode="json")

    if conflict_type == "ambiguous_basement_range":
        options = context.get("options") or []
        for option in options:
            if normalized == normalize_text(option):
                levels = [part.strip() for part in option.split(",") if part.strip()]
                set_levels(task.plan, levels)
                pending["status"] = "resolved"
                task.pending_clarification = None
                if task.status == "needs_clarification":
                    task.status = "collecting"
                result = ReducerResult(
                    handled=True, action="set", slot="levels", changes={"levels": levels},
                    message="Done — set Levels to " + ", ".join(levels) + ".",
                    changed_slots=["levels"], confidence=0.9, plan_mutated=True, normalization=plan_normalization_report(task.plan),
                )
                return "clarification_resolved", result.message, True, False, "clarification_answer_resolved", result.model_dump(mode="json")

    return None

def handle_pending_clarification(task: ActiveTask, text: str) -> tuple[str, str, bool, bool, str | None, dict | None]:
    """Return (route, message, resolved_or_closed, blocked, reason, reducer_result).

    Alpha.2 supports a tiny test-choice resolver and blocks risky actions while
    clarification is open. It does not execute Builder/Formatter/QA engines.
    """
    natural_action = detect_active_task_action_language(text)
    action = get_action_alias(text) or (natural_action.action if natural_action.matched else None) or _detect_pending_risky_action_text(text)
    pending = task.pending_clarification or {}
    prompt = pending.get("prompt") or "Please answer the current clarification before continuing."

    if action == "review":
        return "active_task_review", f"Current task is waiting on clarification. Pending question: {prompt}", False, False, "review_allowed_while_pending", None

    if action == "cancel":
        pending["status"] = "cancelled"
        task.pending_clarification = None
        if task.status == "needs_clarification":
            task.status = "collecting"
        return "clarification_cancelled", "Clarification cancelled. The active task remains open.", True, False, "clarification_cancelled", None

    if action == "cancel_task":
        pending["status"] = "cancelled"
        task.pending_clarification = None
        task.status = "cancelled"
        return "active_task_cancelled", "Current task cancelled safely.", True, False, "task_cancelled_while_pending", None

    if action == "start_new":
        pending["status"] = "cancelled"
        task.pending_clarification = None
        task.status = "cancelled"
        return "active_task_start_new", "Current task cancelled. You can start a new command.", True, False, "start_new_while_pending", None

    if action in RISKY_ACTIONS:
        return "clarification_blocked_action", f"I need to resolve the current clarification before preview/export or workbook-access checks. Pending question: {prompt}", False, True, "pending_clarification_blocks_risky_action", None

    if pending.get("type") == "test_choice":
        answer_class = _classify_test_choice(text)
        if answer_class in {"a", "b"}:
            pending["status"] = "resolved"
            pending["answer"] = answer_class
            task.pending_clarification = None
            if task.status == "needs_clarification":
                task.status = "collecting"
            return "clarification_resolved", f"Clarification resolved with option {answer_class.upper()}.", True, False, "clarification_answer_resolved", None
        if answer_class == "cancel":
            pending["status"] = "cancelled"
            task.pending_clarification = None
            if task.status == "needs_clarification":
                task.status = "collecting"
            return "clarification_cancelled", "Clarification cancelled. The active task remains open.", True, False, "clarification_cancelled", None

    if pending.get("resolver_name") in {"resolve_parser_conflict_guard", "resolve_trade_profile_registry_clarification"}:
        resolved = _resolve_parser_conflict(task, pending, text)
        if resolved is not None:
            return resolved

    if pending.get("type") == "zone_replace_confirmation":
        plan, reducer_result = resolve_zone_replace_confirmation(task.plan, pending, text)
        if reducer_result.handled and reducer_result.action in {"replace", "replace_confirmed", "append", "cancelled", "replace_failed"}:
            task.plan = plan
            pending["status"] = "resolved" if reducer_result.action != "cancelled" else "cancelled"
            task.pending_clarification = None
            if task.status == "needs_clarification":
                task.status = "collecting"
            if reducer_result.action == "cancelled":
                return "clarification_cancelled", reducer_result.message, True, False, "clarification_cancelled", reducer_result.model_dump(mode="json")
            return "clarification_resolved", reducer_result.message, True, False, "clarification_answer_resolved", reducer_result.model_dump(mode="json")

    pending["repeats"] = int(pending.get("repeats") or 0) + 1
    task.pending_clarification = pending
    return "clarification_gate", f"Please answer the current clarification first: {prompt}", False, False, "pending_clarification_repeat", None
