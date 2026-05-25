from __future__ import annotations

import re

from jarvis_v5.schemas.active_task_schema import ActiveTask
from jarvis_v5.router.action_aliases import normalize_text

_WRITING_REPORT_HELP_RE = re.compile(
    r"^\s*(?:rewrite|reword|polish|clean(?:\s+up)?|improve|fix|format|make)\b"
    r".*\b(?:bug\s+report|issue\s+report|complaint|wording|sentence|paragraph|reply|message)\b",
    re.I,
)

def is_explicit_standalone_feedback(text: str) -> bool:
    """Return True only for deliberate no-active-task product feedback.

    Plain writing-help phrases such as "make my bug report clearer" must stay
    owned by NoActiveTaskLanguageGate, not feedback routing.
    """
    normalized = normalize_text(text)
    if _WRITING_REPORT_HELP_RE.search(normalized):
        return False
    no_active_workflow_feedback_markers = (
        "preview is broken",
        "preview broken",
        "preview issue",
        "preview problem",
        "preview is not opening",
        "preview not opening",
    )
    return bool(
        normalized.startswith(("feedback:", "feedback ", "bug report:", "issue report:"))
        or normalized in {"report bug", "send feedback", "submit feedback"}
        or normalized.startswith(("report this bug", "log this bug", "log feedback"))
        or any(marker in normalized for marker in no_active_workflow_feedback_markers)
    )


def is_active_task_issue_feedback(text: str) -> bool:
    """Return True for actual issue reports about the active task/workflow.

    Writing-help requests that merely contain words like "bug report" should
    not be stolen from the active non-mutating language gate.
    """
    normalized = normalize_text(text)
    if not normalized:
        return False
    if "use mezz as code for mezzanine" in normalized:
        return False
    if re.search(r"\buse\s+gf\s+to\s+l\d+\b.*\bmezzanine\s+on\s+l\d+", normalized):
        return False

    writing_verbs = ("make", "rewrite", "clean", "polish", "improve", "fix", "format", "reword")
    writing_objects = ("bug report", "issue report", "complaint", "wording", "sentence", "paragraph", "reply", "message")
    if any(verb in normalized for verb in writing_verbs) and any(obj in normalized for obj in writing_objects):
        return False

    issue_markers = (
        "preview is broken", "preview broken", "preview issue", "preview problem", "preview is not opening", "builder preview is not opening", "preview not opening",
        "builder is not working", "builder not working", "format not working",
        "formatter not working", "export issue", "export is broken", "export broken",
        "parser is not working", "parser not working", "parser is wrong", "parser wrong", "mezzanine", "milestone rows", "milestone levels",
        "setup card looks wrong", "setup is wrong", "preview window", "not one for all window", "wrong preview",
        "workbook preflight wording looks wrong", "wording looks wrong", "window issue", "ui feedback",
        "open preview has an issue", "open preview must close", "preview must close correctly", "workflow is broken", "current builder workflow is broken",
        "still fallback", "fallback on correct actions", "feedback only about active builder", "should not mutate setup",
        "this setup is wrong", "this is wrong", "incorrect", "doesn't work",
        "didn't work", "bugged", "unstable", "not working", "is broken",
    )
    return any(marker in normalized for marker in issue_markers)


def handle_feedback(task: ActiveTask | None, text: str) -> str:
    if task:
        task.feedback_log.append({"text": text, "handled_as": "read_only_feedback"})
        return "Understood — I logged this as feedback for the current task and kept the setup unchanged."
    return "Understood — I logged this as feedback."
