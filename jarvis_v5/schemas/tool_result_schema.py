from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class OutputRecord(BaseModel):
    output_id: str
    tool: str
    source_task_id: str | None = None
    source_workbook: str | None = None
    output_path: str | None = None
    download_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    temporary: bool = False
    next_recommended_tools: list[str] = Field(default_factory=list)
    created_at: str
    retention_days: int = 90


class ToolResult(BaseModel):
    success: bool
    status: Literal["ok", "blocked", "failed"] = "ok"
    message: str
    output_record: OutputRecord | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
