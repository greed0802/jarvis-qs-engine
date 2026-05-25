from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ReducerResult(BaseModel):
    handled: bool = False
    action: str | None = None
    slot: str | None = None
    changes: dict[str, Any] = Field(default_factory=dict)
    requires_clarification: bool = False
    clarification: dict[str, Any] | None = None
    message: str = ""
    warnings: list[str] = Field(default_factory=list)
    changed_slots: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    conflict_type: str | None = None
    conflicting_slots: list[str] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    options: list[str] = Field(default_factory=list)
    plan_mutated: bool | None = None
    normalization: dict[str, Any] | None = None
    trade_registry: dict[str, Any] | None = None
