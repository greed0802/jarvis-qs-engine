from __future__ import annotations

"""Active-task non-mutating language gate for alpha.22.2E.

This module is side-effect free. It only classifies active Builder messages that
are clearly conversational/help/writing requests and should not enter the slot
reducer. It never mutates a Builder plan and never takes confidence-engine
control.
"""

import re
from dataclasses import dataclass
from typing import Any

from jarvis_v5.router.action_aliases import normalize_text
from jarvis_v5.router.no_active_task_language_gate import (
    negative_guard_detail,
    public_negative_guard_for_detail,
    detect_general_qs_help,
)
from jarvis_v5.router.engineering_language_gate import classify_engineering_language


@dataclass(frozen=True)
class ActiveTaskLanguageDecision:
    matched: bool = False
    category: str = "none"  # greeting | thanks | writing_help | casual_non_tool | general_qs_help | general_costx_help | engineering_help | engineering_unit_help | none
    route: str = "no_decision"
    intent: str = "GENERAL"
    confidence: int = 0
    reason: str = "no_active_task_language_match"
    public_negative_guard: str | None = None
    negative_guard_detail: str | None = None
    tool_candidates: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "matched": self.matched,
            "category": self.category,
            "route": self.route,
            "intent": self.intent,
            "confidence": self.confidence,
            "reason": self.reason,
            "tool_candidates": list(self.tool_candidates),
            "plan_mutated": False,
        }
        if self.public_negative_guard:
            payload["negative_guard"] = self.public_negative_guard
        if self.negative_guard_detail:
            payload["negative_guard_detail"] = self.negative_guard_detail
        return payload


_GREETING_RE = re.compile(r"^(?:hi|hello|hey|good\s+(?:morning|afternoon|evening)|yo|sup)(?:\s+jarvis)?[.! ]*$", re.I)
_THANKS_RE = re.compile(r"^(?:thanks?|thank\s+you|ok(?:ay)?\s+thanks?|cheers|nice|good|great)[.! ]*$", re.I)

_HELP_NON_MUTATING_RE = re.compile(
    r"\b(?:help\s+me\s+understand|what\s+does|explain|meaning\s+of)\b.*\b(?:levels?|zone|head|registry\s+advisory|builder|boq|costx|unit|setup)\b|\bdo\s+not\s+mutate\b|\bwithout\s+changing\b",
    re.I,
)



_ACTIVE_WORKBOOK_READ_POLICY_HELP_RE = re.compile(
    r"(?:"
    r"\b(?:what\s+is|what\s+does|why\s+(?:are|is)|explain|tell\s+me\s+(?:why|about)?|review|check)\b.*\b(?:workbook[_\s-]*read\s+policy|cells?_read|formulas?_read|current_access_tier|sheet[_\s-]*name\s+probe|sheet-name\s+probe|cell\s+read|future\s+limited\s+cell\s+range\s+read|workbook_parse_enabled|formula\s+token\s+policy|metadata\s+probe|next\s+safe\s+action|workbook\s+reading|sheet_name_probe_only|preview\s+readiness|export\s+readiness|workbook\s+read\s+safety\s+boundary)\b|"
    r"\bwhat\s+is\s+allowed\b.*\b(?:metadata\s+probe|workbook\s+read(?:ing)?|cell\s+read|formula\s+read)\b|"
    r"\bwhy\s+is\s+current\s+tier\s+sheet_name_probe_only\b|"
    r"\bexplain\s+the\s+current\s+workbook\s+read\s+safety\s+boundary\b"
    r")",
    re.I,
)


_ACTIVE_CONTENT_READ_ATTACK_RE = re.compile(
    r"(?:"
    r"\b(?:developer\s+override|system\s*:|bypass\s+policy|ignore\s+safety|forget\s+no[-\s]*engine\s+locks)\b|"
    r"\b(?:formulas?_read|cells?_read|workbook_read_enabled|workbook_parse_enabled)\s*(?:=|true|on|enabled)\b|"
    r"\b(?:set|turn|make|force|enable)\b.*\b(?:formulas?_read|cells?_read|workbook_read_enabled|workbook_parse_enabled)\b.*\b(?:true|on|enabled)\b|"
    r"\b(?:call|use)\s+openpyxl\b|"
    r"\b(?:parse|open|read|scan|extract|list|get)\b.*\b(?:workbook\s+contents?|preview\s+data|saved_path|raw_path|cells?|formulas?|cached\s+values?|dimensions?|used\s+ranges?|hidden\s+sheets?|comments?|tables?|styles?)\b|"
    r"\b(?:open|use)\b.*\b(?:saved_path|raw_path)\b|"
    r"\blegacy\s+builder\b.*\b(?:kill\s+switch|active|call|use|run)\b|"
    r"\bkill\s+switch\b.*\blegacy\s+builder\b|"
    r"\btreat\s+sheet\s+names\s+as\s+permission\s+to\s+read\s+cells\b|"
    r"\bsilently\s+read\s+dimensions\b"
    r")",
    re.I,
)

_ACTIVE_CONTENT_READ_POLICY_HELP_HINT_RE = re.compile(
    r"\b(?:what\s+is|what\s+does|why\s+(?:are|is)|explain|tell\s+me|review|check)\b",
    re.I,
)


def detect_active_task_content_read_attack(text: str) -> bool:
    """Return True for direct active-task workbook-content read/bypass commands.

    This is side-effect free and intentionally excludes policy/help questions,
    which remain owned by is_active_task_non_mutating_language().
    """
    normalized = normalize_text(text or "")
    if not normalized:
        return False
    if _ACTIVE_CONTENT_READ_POLICY_HELP_HINT_RE.search(normalized) and _ACTIVE_WORKBOOK_READ_POLICY_HELP_RE.search(normalized):
        return False
    return bool(_ACTIVE_CONTENT_READ_ATTACK_RE.search(normalized))

_ACTIVE_BUILDER_CONCEPT_HELP_RE = re.compile(
    r"(?:"
    r"\b(?:tell\s+me\s+why|why)\b.*\bworkbook[_\s-]*read\b.*\b(?:false|disabled|off|blocked|safe|safety)\b|"
    r"\b(?:explain|what\s+is|what\s+does|tell\s+me\s+about)\b.*\b(?:current\s+)?safety\s+boundary\b|"
    r"\b(?:what\s+is|explain|tell\s+me\s+about)\b.*\badapter\s+dry\s+run\b|"
    r"\b(?:explain|what\s+is|tell\s+me\s+about)\b.*\bcontract[-\s]*only\s+stage\b|"
    r"\b(?:what\s+does|what\s+is|explain|tell\s+me\s+about)\b.*\bformula\s+integrity\s+guard\b|"
    r"\b(?:why|explain|tell\s+me\s+why)\b.*\bpreview\b.*\bapproval[-\s]*based\b|"
    r"\b(?:what\s+is|explain|tell\s+me\s+about)\b.*\bbuilder\s*run\s*snapshot\b"
    r")",
    re.I,
)

_GENERAL_COSTX_RE = re.compile(
    r"\b(?:what\s+is|what's|explain|tell\s+me\s+about|how\s+does)\b.*\b(?:costx|costx\s+functions?|xgetwallarea|xgetcount|xgetcustom)\b",
    re.I,
)

_SETUP_COMMAND_RE = re.compile(
    r"^\s*(?:use|set|change|switch|make|apply|select|replace|add)\b.*\b(?:wall\s*types?|doors?|windows?|structural\s+steel|steel\s+surface\s+area|concrete|reo|reinforcement|reinforcement\s+weight|formworks?|xgetwallarea|xgetcount|xgetcustom|count|unit|zone\s*\d+|head\s*[1-4]|levels?|trade|function)\b|"
    r"\b(?:zone\s*\d+\s*:|unit\s+(?:no|nr|count|item|each|pcs|m2|m²|m3|m³|lm|m|t|kg|sqm|sq\.?\s*m|sq\s+met(?:re|er)s?|square\s+met(?:re|er)s?)|head\s*[1-4]\s+for\s+zone|levels?\s+(?:gf|b\d+|l\d+|from|are|is|should|to)|trade\s+(?:should\s+be|is)|function\s+(?:should\s+be|is))\b",
    re.I,
)


def is_explicit_setup_command_text(text: str) -> bool:
    normalized = normalize_text(text or "")
    # Engineering QA/unit-audit wording can contain tokens like "use unit psi"
    # without being a Builder setup mutation. Keep those under the active
    # non-mutating language gate unless the wording is a clear Builder slot edit.
    if re.search(r"\b(?:engineering\s+qa|engineering\s+units?|unit\s+audit|pressure\s+units?|structural\s+(?:terms?|notes?))\b", normalized, flags=re.I):
        return False
    if re.search(r"\b(?:help\s+me\s+understand|what\s+does|explain|meaning\s+of|do\s+not\s+mutate|without\s+changing)\b", normalized, flags=re.I):
        return False
    if _SETUP_COMMAND_RE.search(normalized):
        return True
    natural_setup_patterns = (
        r"\b(?:the\s+)?unit\s+(?:should\s+be|is|as|to|=)\s+(?:no|nr|count|item|each|pcs|m2|m²|m3|m³|lm|m|t|kg|sqm|sq\.?\s*m|sq\s+met(?:re|er)s?|square\s+met(?:re|er)s?)\b",
        r"\b(?:for\s+now,?\s*)?zone\s+\d+\s+(?:is|are|has|have|contains?|should\s+(?:include|contain))\b",
        r"\b(?:please\s+)?put\s+zone\s+\d+\s+(?:under|at|to|in)\s+head\s*[1-4]\b",
        r"\b(?:please\s+)?put\s+.+?\s+(?:under|in|inside|into|at|to)\s+zone\s+\d+\b",
        r"\b.+?\s+(?:are|is|should\s+be|should\s+go|go(?:es)?)\s+(?:in|inside|under|at|to)?\s*zone\s+\d+\b",
        r"\b(?:for\s+)?zone\s+\d+\s+(?:use|set|take|has|have)\s+.+",
        r"\bzone\s+\d+\s+(?:goes\s+under|should\s+be|is|at)\s+head\s*[1-4]\b",
        r"\bhead\s*[1-4]\s+(?:should\s+be\s+)?(?:is\s+)?(?:for|to|under)\s+zone\s+\d+\b",
        r"\bhead\s*[1-4]\s+belongs\s+to\s+zone\s+\d+\b",
        r"\b(?:use|set)?\s*(?:the\s+)?levels?\s+(?:should\s+be|are|is|from|as)?\s*[a-z0-9 ,]+\s+to\s+[a-z0-9 ]+",
    )
    return any(re.search(pattern, normalized, flags=re.I) for pattern in natural_setup_patterns)


def is_active_task_non_mutating_language(text: str) -> ActiveTaskLanguageDecision:
    normalized = normalize_text(text)
    if not normalized:
        return ActiveTaskLanguageDecision()

    if _ACTIVE_WORKBOOK_READ_POLICY_HELP_RE.search(normalized):
        return ActiveTaskLanguageDecision(
            matched=True,
            category="workbook_read_policy_help",
            route="active_task_non_mutating_language",
            intent="ACTIVE_TASK_NON_MUTATING_LANGUAGE",
            confidence=98,
            reason="active_task_non_mutating:workbook_read_policy_help",
        )

    if _HELP_NON_MUTATING_RE.search(normalized) or _ACTIVE_BUILDER_CONCEPT_HELP_RE.search(normalized):
        return ActiveTaskLanguageDecision(
            matched=True,
            category="active_help_no_mutation",
            route="active_task_non_mutating_language",
            intent="ACTIVE_TASK_NON_MUTATING_LANGUAGE",
            confidence=98,
            reason="active_task_non_mutating:help_no_mutation",
        )

    if _GREETING_RE.search(normalized):
        return ActiveTaskLanguageDecision(
            matched=True,
            category="greeting",
            route="active_task_non_mutating_language",
            intent="ACTIVE_TASK_NON_MUTATING_LANGUAGE",
            confidence=98,
            reason="active_task_non_mutating:greeting",
        )

    if _THANKS_RE.search(normalized):
        return ActiveTaskLanguageDecision(
            matched=True,
            category="thanks",
            route="active_task_non_mutating_language",
            intent="ACTIVE_TASK_NON_MUTATING_LANGUAGE",
            confidence=98,
            reason="active_task_non_mutating:thanks",
        )

    detail = negative_guard_detail(normalized)
    if detail:
        public = public_negative_guard_for_detail(detail)
        category = "writing_help" if public == "format_text_not_workbook" else "casual_non_tool"
        return ActiveTaskLanguageDecision(
            matched=True,
            category=category,
            route="active_task_non_mutating_language",
            intent="ACTIVE_TASK_NON_MUTATING_LANGUAGE",
            confidence=98,
            reason=f"active_task_non_mutating:{category}",
            public_negative_guard=public,
            negative_guard_detail=detail,
        )

    qs_help = detect_general_qs_help(normalized)
    if qs_help.matched:
        return ActiveTaskLanguageDecision(
            matched=True,
            category="general_qs_help",
            route="active_task_non_mutating_language",
            intent="ACTIVE_TASK_NON_MUTATING_LANGUAGE",
            confidence=qs_help.confidence,
            reason=f"active_task_non_mutating:{qs_help.reason}",
            tool_candidates=qs_help.tool_candidates,
        )

    if _GENERAL_COSTX_RE.search(normalized):
        return ActiveTaskLanguageDecision(
            matched=True,
            category="general_costx_help",
            route="active_task_non_mutating_language",
            intent="ACTIVE_TASK_NON_MUTATING_LANGUAGE",
            confidence=94,
            reason="active_task_non_mutating:costx_general_help",
        )

    engineering = classify_engineering_language(normalized)
    if engineering.matched:
        return ActiveTaskLanguageDecision(
            matched=True,
            category=engineering.category,
            route="active_task_non_mutating_language",
            intent="ACTIVE_TASK_NON_MUTATING_LANGUAGE",
            confidence=engineering.confidence,
            reason=f"active_task_non_mutating:{engineering.reason}",
            tool_candidates=engineering.tool_candidates,
        )

    return ActiveTaskLanguageDecision()
