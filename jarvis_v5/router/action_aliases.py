from __future__ import annotations

import re

ACTION_ALIASES = {
    "review": {"review", "show setup", "review setup", "review current setup", "review the current setup", "current setup", "what is the task"},
    "preview": {"preview", "open preview"},
    "approve_preview": {"approve", "approved", "approve and preview", "approve & preview", "approve preview"},
    "export": {"export", "run export"},
    "download": {"download", "download output"},
    "cancel_task": {"cancel task", "stop this", "stop task"},
    "cancel": {"cancel"},
    "start_new": {"start new", "new command", "new task", "start new command"},
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def get_action_alias(text: str) -> str | None:
    normalized = re.sub(r"[.!?]+$", "", normalize_text(text)).strip()
    for action, aliases in ACTION_ALIASES.items():
        if normalized in aliases:
            return action
    return None
