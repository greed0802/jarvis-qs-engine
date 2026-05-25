from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class TestFileSpec(BaseModel):
    __test__ = False
    field: str = "file"
    path: str
    filename: str | None = None
    content_type: str = "application/octet-stream"


class TestStep(BaseModel):
    __test__ = False
    model_config = ConfigDict(populate_by_name=True)
    name: str
    method: Literal["GET", "POST"]
    endpoint: str
    json_body: dict[str, Any] | None = Field(default=None, alias="json")
    form: dict[str, Any] | None = None
    data: dict[str, Any] | None = None
    file_fixture: str | None = None
    files: list[TestFileSpec] = Field(default_factory=list)
    assertions: list[dict[str, Any]] = Field(default_factory=list)
    save: dict[str, str] = Field(default_factory=dict)


class TestCase(BaseModel):
    __test__ = False
    name: str
    reset_conversation: bool = False
    steps: list[TestStep]


class TestPack(BaseModel):
    __test__ = False
    pack_name: str
    pack_format: Literal["multi_step", "single_request"] = Field(default="multi_step", alias="format")
    version_target: str | None = None
    base_url: str | None = None
    tests: list[TestCase]
