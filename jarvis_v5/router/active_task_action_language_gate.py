from __future__ import annotations

"""Natural active-task action language gate.

Side-effect free. It only classifies active-task Review / Preview / Export /
Download language. MainRouter remains the sole final route owner.
"""

import re
from dataclasses import dataclass
from typing import Any

from jarvis_v5.router.action_aliases import normalize_text


@dataclass(frozen=True)
class ActiveTaskActionDecision:
    matched: bool = False
    action: str | None = None
    route_hint: str | None = None
    confidence: int = 0
    reason: str = "no_active_task_action_language_match"
    alias: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "matched": self.matched,
            "action": self.action,
            "route_hint": self.route_hint,
            "confidence": self.confidence,
            "reason": self.reason,
        }
        if self.alias:
            payload["alias"] = self.alias
        return payload


def _clean(text: str) -> str:
    # Keep alpha.24 normalization but remove common testing wrappers that should
    # not prevent active-action ownership.
    normalized = normalize_text(text)
    normalized = re.sub(r"^[,\s]*(?:please|safely|no engine|before anything else|for this active task|in jarvis|as a qs command)[:,\s]+", "", normalized)
    normalized = re.sub(r"\s+(?:please|with approval first|in the current workflow|and keep no-engine safety|but do not read workbook|before export|do not fallback)\.?$", "", normalized)
    normalized = re.sub(r"\s+—\s+do not fallback$", "", normalized)
    return normalized.strip(" .")


def _decision(action: str, alias: str, confidence: int = 96) -> ActiveTaskActionDecision:
    route_hint = {
        "review": "active_task_review",
        "preview": "active_task_preview_stub",
        "export": "active_task_export_stub",
        "download": "active_task_action_stub",
    }.get(action, "active_task_action_stub")
    return ActiveTaskActionDecision(
        matched=True,
        action=action,
        route_hint=route_hint,
        confidence=confidence,
        reason=f"active_task_action_language:{action}",
        alias=alias,
    )


_REVIEW_RE = re.compile(
    r"(?:"
    r"\breview\b.*\b(?:setup|plan|task|summary|details|current|builder)\b|"
    r"\b(?:check|show|give|display|summarize|summarise|need)\b.*\b(?:current\s+)?(?:builder\s+)?(?:setup|plan|task|details|summary|understand|understanding)\b|"
    r"\b(?:setup|plan|task)\s+review\b|"
    r"\bwhat\s+(?:do\s+you\s+)?(?:currently\s+)?(?:understand|have)\b|"
    r"\breview\b.*\b(?:what\s+we\s+have|setup)\b|"
    r"\bbefore\s+preview\b.*\breview\b"
    r")",
    re.I,
)

_PREVIEW_RE = re.compile(
    r"(?:"
    r"\bpreview\b|"
    r"\b(?:show|open|generate|run|create)\b.*\bpreview\b|"
    r"\bcan\s+i\s+see\s+(?:the\s+)?preview\b|"
    r"\bpreview\s+(?:stub|when\s+ready|safely|only)\b"
    r")",
    re.I,
)

_EXPORT_RE = re.compile(
    r"(?:"
    r"\bexport\b|"
    r"\b(?:downloadable|final)\s+export\b|"
    r"\b(?:run|do|create|prepare)\b.*\bexport\b|"
    r"\bexport\s+(?:it|this|current|builder|output|status|stub)\b"
    r")",
    re.I,
)



_WRITING_REPORT_HELP_RE = re.compile(
    r"^\s*(?:rewrite|reword|polish|clean(?:\s+up)?|improve|fix|format|make)\b"
    r".*\b(?:bug\s+report|issue\s+report|complaint|wording|sentence|paragraph|reply|message)\b",
    re.I,
)

_EXPLANATORY_ACTION_WORDING_RE = re.compile(
    r"^\s*(?:why|what\s+is|what\s+does|explain|tell\s+me\s+why|how\s+does)\b.*\b(?:preview|export|download|review|approval)\b",
    re.I,
)
_EXPLICIT_ACTION_VERB_RE = re.compile(
    r"\b(?:run|open|generate|create|do|prepare|start|execute|export|download|preview|review)\b",
    re.I,
)

_DOWNLOAD_RE = re.compile(
    r"(?:"
    r"\bdownload\b|"
    r"\b(?:show|give|open|where\s+is)\b.*\b(?:output\s+file|file\s+output|download|download\s+link|latest\s+(?:generated\s+)?file|current\s+result|current\s+builder\s+output)\b|"
    r"\b(?:output\s+download\s+link|latest\s+download|file\s+output)\b"
    r")",
    re.I,
)


def detect_active_task_action_language(text: str) -> ActiveTaskActionDecision:
    normalized = _clean(text)
    if not normalized:
        return ActiveTaskActionDecision()

    if _EXPLANATORY_ACTION_WORDING_RE.search(normalized) and not re.match(r"^\s*(?:preview|export|download|review|open|run|generate|create|prepare|do)\b", normalized, flags=re.I):
        return ActiveTaskActionDecision()

    # Writing/report-help phrases may contain words like Preview/Export as
    # quoted issue content. They are non-mutating language, not actions.
    if _WRITING_REPORT_HELP_RE.search(normalized):
        return ActiveTaskActionDecision()

    # Order matters: review-before-preview handles phrases like
    # "Before preview, review this setup". Download remains before export.
    if _REVIEW_RE.search(normalized) or re.fullmatch(r"review(?:\s+(?:it|this))?", normalized):
        return _decision("review", "natural_review_setup", 97)
    if _DOWNLOAD_RE.search(normalized):
        return _decision("download", "natural_download", 96)
    if _PREVIEW_RE.search(normalized):
        return _decision("preview", "natural_preview", 97)
    if _EXPORT_RE.search(normalized):
        return _decision("export", "natural_export", 96)
    return ActiveTaskActionDecision()
