from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

TaskStatus = Literal[
    "collecting",
    "waiting_for_file",
    "needs_clarification",
    "needs_review",
    "plan_ready",
    "preview_running",
    "preview_ready",
    "export_running",
    "export_ready",
    "failed",
    "cancelled",
]

ToolName = Literal["builder", "formatter", "qa", "description", "final_qa", "jarvis_chat"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ActiveTask(BaseModel):
    task_id: str
    conversation_id: str
    tool: ToolName
    status: TaskStatus = "collecting"
    workbook: dict[str, Any] | None = None
    plan: dict[str, Any] = Field(default_factory=dict)
    pending_clarification: dict[str, Any] | None = None
    preview_result: dict[str, Any] | None = None
    export_result: dict[str, Any] | None = None
    adapter_dry_run_result: dict[str, Any] | None = None
    output_ids: list[str] = Field(default_factory=list)
    feedback_log: list[dict[str, Any]] = Field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def touch(self) -> None:
        timestamp = now_iso()
        if not self.created_at:
            self.created_at = timestamp
        self.updated_at = timestamp
