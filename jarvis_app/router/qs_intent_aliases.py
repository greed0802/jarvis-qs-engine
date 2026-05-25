from __future__ import annotations

import re
from dataclasses import dataclass

from jarvis_v5.router.action_aliases import normalize_text
from jarvis_v5.router.no_active_task_language_gate import detect_builder_start_alias, detect_generic_tool_ambiguity, negative_guard_detail


@dataclass(frozen=True)
class QSAliasResult:
    matched: bool
    alias: str | None = None
    canonical_intent: str | None = None
    confidence: int = 0
    region_hint: str | None = None
    requires_setup: bool = True
    negative_guard: str | None = None
    tool_candidates: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "matched": self.matched,
            "alias": self.alias,
            "canonical_intent": self.canonical_intent,
            "confidence": self.confidence,
            "region_hint": self.region_hint,
            "requires_setup": self.requires_setup,
            "negative_guard": self.negative_guard,
            "tool_candidates": list(self.tool_candidates),
        }


_CREATE_VERBS = r"(?:create|prepare|make|build|start|set up|setup|generate|draft|produce|help me create|help me prepare)"
_QS_CONTEXT = r"(?:boq|bq|bill of quantities|schedule of values|schedule of quantities|schedule of works|trade schedule|quantity schedule|measurement schedule|tender boq|base sheet|costx|nrm|smm|takeoff|take off|estimate|priced boq|unpriced boq)"



_EXPLICIT_RESET_PATTERNS = [
    r"\b(start|create|make|begin)\s+(a\s+)?new\b",
    r"\b(new\s+boq|new\s+task|new\s+command|new\s+project)\b",
    r"\b(discard|reset|cancel)\s+(this|current)\b",
]



def negative_guard_reason(text: str) -> str | None:
    return negative_guard_detail(text)


def is_explicit_new_task_request(text: str) -> bool:
    normalized = normalize_text(text)
    return any(re.search(pattern, normalized) for pattern in _EXPLICIT_RESET_PATTERNS)


def detect_qs_builder_start_alias(text: str) -> QSAliasResult:
    decision = detect_builder_start_alias(text)
    if not decision.matched:
        return QSAliasResult(
            False,
            negative_guard=decision.negative_guard_detail or decision.public_negative_guard,
        )
    return QSAliasResult(
        True,
        alias=decision.alias,
        canonical_intent="builder_start",
        confidence=decision.confidence,
        region_hint=decision.region_hint,
        requires_setup=True,
        negative_guard=decision.negative_guard_detail,
        tool_candidates=decision.tool_candidates or ("builder",),
    )


def detect_tool_like_ambiguity(text: str) -> QSAliasResult:
    decision = detect_generic_tool_ambiguity(text)
    if not decision.matched:
        return QSAliasResult(
            False,
            negative_guard=decision.negative_guard_detail or decision.public_negative_guard,
        )
    return QSAliasResult(
        True,
        alias=decision.alias,
        canonical_intent="tool_like_ambiguous",
        confidence=decision.confidence,
        requires_setup=decision.requires_setup,
        negative_guard=decision.negative_guard_detail,
        tool_candidates=decision.tool_candidates,
    )
