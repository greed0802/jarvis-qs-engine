from __future__ import annotations

"""Router confidence scoring for alpha.22.2C.

The confidence scorer remains side-effect free. Alpha.22.2C uses the same
no-active-task language classification source as MainRouter so diagnostics and
runtime routing do not drift. It never creates tasks, mutates Builder plans,
binds attachments, or calls Builder/Formatter/QA/O&A engines.
"""

from dataclasses import dataclass
from typing import Any

from jarvis_v5.router.action_aliases import normalize_text
from jarvis_v5.router.qs_intent_aliases import detect_tool_like_ambiguity
from jarvis_v5.router.no_active_task_language_gate import classify_no_active_task_language


@dataclass(frozen=True)
class ConfidenceScore:
    enabled: bool = True
    mode: str = "shadow"
    would_route: str = "general_stub"
    would_confidence: int = 60
    confidence_reason: str = "no_strong_tool_signal"
    tool_candidates: tuple[str, ...] = ()
    negative_guard: str | None = None
    negative_guard_detail: str | None = None
    requires_clarification: bool = False
    control_taken: bool = False

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "enabled": self.enabled,
            "mode": self.mode,
            "would_route": self.would_route,
            "would_confidence": self.would_confidence,
            "confidence_reason": self.confidence_reason,
            "tool_candidates": list(self.tool_candidates),
            "requires_clarification": self.requires_clarification,
            "control_taken": self.control_taken,
        }
        if self.negative_guard is not None:
            payload["negative_guard"] = self.negative_guard
        if self.negative_guard_detail is not None:
            payload["negative_guard_detail"] = self.negative_guard_detail
        return payload


def _score_from_no_active_decision(text: str) -> ConfidenceScore | None:
    decision = classify_no_active_task_language(text)
    if not decision.matched:
        return None
    if decision.category == "writing_help":
        return ConfidenceScore(
            would_route="general_writing_help",
            would_confidence=decision.confidence,
            confidence_reason=decision.reason,
            tool_candidates=decision.tool_candidates,
            negative_guard=decision.public_negative_guard,
            negative_guard_detail=decision.negative_guard_detail,
            requires_clarification=decision.requires_clarification,
        )
    return ConfidenceScore(
        would_route=decision.route,
        would_confidence=decision.confidence,
        confidence_reason=decision.reason,
        tool_candidates=decision.tool_candidates,
        negative_guard=decision.public_negative_guard,
        negative_guard_detail=decision.negative_guard_detail,
        requires_clarification=decision.requires_clarification,
    )


def score_route_candidates(
    text: str,
    *,
    has_active_task: bool = False,
    active_tool: str | None = None,
    has_pending_clarification: bool = False,
    has_attachments: bool = False,
) -> dict[str, Any]:
    """Return a read-only route recommendation for router diagnostics."""
    normalized = normalize_text(text)
    if not normalized:
        return ConfidenceScore(
            would_route="general_stub",
            would_confidence=70,
            confidence_reason="empty_text",
        ).as_dict()

    if has_pending_clarification:
        return ConfidenceScore(
            would_route="pending_clarification_gate",
            would_confidence=100,
            confidence_reason="pending_clarification_context_active",
            tool_candidates=((active_tool or "builder"),),
            requires_clarification=True,
        ).as_dict()

    if has_active_task:
        tool = active_tool or "builder"
        tool_ambiguity = detect_tool_like_ambiguity(normalized)
        if tool_ambiguity.matched:
            route = "formatter_handoff_needs_confirmation" if "formatter" in tool_ambiguity.tool_candidates else "active_task_slot_edit_needs_clarification"
            return ConfidenceScore(
                would_route=route,
                would_confidence=98,
                confidence_reason=f"active_task_present + ambiguous_tool_phrase:{tool_ambiguity.alias}",
                tool_candidates=tuple(tool_ambiguity.tool_candidates or (tool,)),
                requires_clarification=True,
            ).as_dict()
        if normalized in {"same", "use this", "this one", "that one", "ok use it"}:
            return ConfidenceScore(
                would_route="active_task_slot_edit_needs_clarification",
                would_confidence=98,
                confidence_reason="active_task_present + ambiguous_short_reply",
                tool_candidates=(tool,),
                requires_clarification=True,
            ).as_dict()
        return ConfidenceScore(
            would_route="active_task_context",
            would_confidence=90,
            confidence_reason=f"active_task_present:{tool}",
            tool_candidates=(tool,),
            requires_clarification=False,
        ).as_dict()

    decision_score = _score_from_no_active_decision(normalized)
    if decision_score is not None:
        return decision_score.as_dict()

    if has_attachments:
        return ConfidenceScore(
            would_route="choose_tool",
            would_confidence=88,
            confidence_reason="attachment_present_no_active_task_needs_tool_choice",
            tool_candidates=("builder", "formatter", "qa_checker"),
            requires_clarification=True,
        ).as_dict()

    return ConfidenceScore(
        would_route="general_stub",
        would_confidence=70,
        confidence_reason="no_strong_tool_signal",
        tool_candidates=(),
        requires_clarification=False,
    ).as_dict()


LIMITED_CONTROL_ROUTES = {
    "new_builder_task_shell",
    "choose_tool",
    "general_stub",
    "general_chat",
    "general_writing_help",
    "registry_advisory_metadata_only",
}


def confidence_engine_can_control(
    *,
    has_active_task: bool,
    has_pending_clarification: bool,
    has_attachments: bool,
    current_route: str,
    score: dict[str, Any] | None,
    minimum_confidence: int = 90,
) -> bool:
    """Return True only for no-active-task limited-control lanes."""
    if has_active_task or has_pending_clarification or has_attachments:
        return False
    if current_route not in {"general_stub", "choose_tool"}:
        return False
    payload = dict(score or {})
    would_route = payload.get("would_route")
    if would_route not in LIMITED_CONTROL_ROUTES:
        return False
    try:
        confidence = int(payload.get("would_confidence") or 0)
    except (TypeError, ValueError):
        confidence = 0
    return confidence >= minimum_confidence


def attach_actual_route(
    confidence_payload: dict[str, Any],
    *,
    actual_route: str,
    control_taken: bool = False,
    mode: str | None = None,
) -> dict[str, Any]:
    payload = dict(confidence_payload or {})
    if mode:
        payload["mode"] = mode
    payload["actual_route"] = actual_route
    payload["route_mismatch"] = bool(payload.get("would_route") and payload.get("would_route") != actual_route)
    payload["control_taken"] = bool(control_taken)
    return payload
