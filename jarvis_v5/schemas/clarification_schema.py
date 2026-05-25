from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class PendingClarification(BaseModel):
    clarification_id: str
    task_id: str
    type: str
    prompt: str
    options: list[str] = Field(default_factory=list)
    expected_answer_classes: list[str] = Field(default_factory=list)
    resolver_name: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    repeats: int = 0
    max_repeats: int = 2
    status: Literal["open", "resolved", "expired", "cancelled"] = "open"
