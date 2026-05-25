from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConversationState(BaseModel):
    conversation_id: str
    project_id: str | None = None
    active_task_id: str | None = None
    active_workbook_id: str | None = None
    pending_clarification_id: str | None = None
    latest_preview_id: str | None = None
    latest_export_id: str | None = None
    current_mode: Literal["ask_first", "autopilot", "manual"] = "ask_first"
    created_at: str = ""
    updated_at: str = ""

    def touch(self) -> None:
        timestamp = now_iso()
        if not self.created_at:
            self.created_at = timestamp
        self.updated_at = timestamp
