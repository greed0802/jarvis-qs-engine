from __future__ import annotations

"""Cached route classification context.

This module is side-effect free. It centralizes repeated text classification so
MainRouter can make one final route decision without re-running independent
owners in separate branches.
"""

from dataclasses import dataclass
from typing import Any

from jarvis_v5.router.action_aliases import get_action_alias, normalize_text
from jarvis_v5.router.active_task_action_language_gate import ActiveTaskActionDecision, detect_active_task_action_language
from jarvis_v5.router.no_active_task_language_gate import NoActiveTaskLanguageDecision, classify_no_active_task_language
from jarvis_v5.router.qs_intent_aliases import detect_qs_builder_start_alias, detect_tool_like_ambiguity, negative_guard_reason


@dataclass(frozen=True)
class RouteContext:
    raw_text: str
    normalized_text: str
    has_active_task: bool
    has_pending_clarification: bool
    has_attachments: bool
    exact_action: str | None
    active_action_language: ActiveTaskActionDecision | None
    action: str | None
    no_active_language: NoActiveTaskLanguageDecision | None
    qs_alias: Any
    tool_ambiguity: Any
    negative_guard: str | None

    def as_trace(self) -> dict[str, Any]:
        return {
            "classification_owner": "main_router_route_context",
            "classification_reused": True,
            "has_active_task": self.has_active_task,
            "has_pending_clarification": self.has_pending_clarification,
            "has_attachments": self.has_attachments,
            "exact_action": self.exact_action,
            "active_action": self.action,
            "active_action_language": self.active_action_language.as_dict() if self.active_action_language else None,
            "no_active_language": self.no_active_language.as_dict() if self.no_active_language else None,
            "negative_guard": self.negative_guard,
        }


def build_route_context(text: str, *, has_active_task: bool, has_pending_clarification: bool, has_attachments: bool) -> RouteContext:
    exact_action = get_action_alias(text)
    active_action_language = detect_active_task_action_language(text) if has_active_task else None
    action = exact_action or (active_action_language.action if active_action_language and active_action_language.matched else None)
    no_active_language = classify_no_active_task_language(text) if not has_active_task and not has_pending_clarification and not has_attachments else None
    return RouteContext(
        raw_text=text or "",
        normalized_text=normalize_text(text or ""),
        has_active_task=has_active_task,
        has_pending_clarification=has_pending_clarification,
        has_attachments=has_attachments,
        exact_action=exact_action,
        active_action_language=active_action_language,
        action=action,
        no_active_language=no_active_language,
        qs_alias=detect_qs_builder_start_alias(text),
        tool_ambiguity=detect_tool_like_ambiguity(text),
        negative_guard=negative_guard_reason(text),
    )
