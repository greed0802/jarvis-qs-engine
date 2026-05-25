from __future__ import annotations

from typing import Literal
from jarvis_v5.router.action_aliases import get_action_alias, normalize_text
from jarvis_v5.router.qs_intent_aliases import detect_qs_builder_start_alias

Intent = Literal["ACTION_ALIAS", "FEEDBACK", "NEW_COMMAND", "ATTACHMENT_ONLY", "GENERAL"]

FEEDBACK_PHRASES = [
    "wrong",
    "not working",
    "bug",
    "bugged",
    "unstable",
    "preview issue",
    "broken",
    "is broken",
    "format not working",
    "parser not working",
    "this is wrong",
    "incorrect",
    "doesn't work",
    "didn't work",
]

NEW_COMMAND_PHRASES = [
    "build",
    "builder",
    "create boq",
    "create me a boq",
    "base boq",
    "base sheet",
    "run qa",
]


def classify_intent(text: str, *, has_attachments: bool = False) -> Intent:
    normalized = normalize_text(text)
    if has_attachments and not normalized:
        return "ATTACHMENT_ONLY"
    if get_action_alias(normalized):
        return "ACTION_ALIAS"
    if any(phrase in normalized for phrase in FEEDBACK_PHRASES):
        return "FEEDBACK"
    if any(phrase in normalized for phrase in NEW_COMMAND_PHRASES):
        return "NEW_COMMAND"
    if detect_qs_builder_start_alias(normalized).matched:
        return "NEW_COMMAND"
    if has_attachments and normalized in {"here", "attached", "done", "use this"}:
        return "ATTACHMENT_ONLY"
    return "GENERAL"
