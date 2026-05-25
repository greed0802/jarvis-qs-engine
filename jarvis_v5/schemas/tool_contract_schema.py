from __future__ import annotations

from pydantic import BaseModel, Field


class ToolSafetyPolicy(BaseModel):
    metadata_only: bool = True
    execution_enabled: bool = False
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False


class ToolContractSpec(BaseModel):
    tool_key: str
    capability_key: str
    input_contract: str
    output_contract: str
    input_contract_fields: list[str] = Field(default_factory=list)
    output_contract_fields: list[str] = Field(default_factory=list)
    required_file_keys: list[str] = Field(default_factory=list)
    approval_gate: str
    route_owner: str
    metadata_only: bool = True
    execution_enabled: bool = False
    workbook_read_required: bool = False
    requires_approval_before_execution: bool = True
    safety_policy: ToolSafetyPolicy = Field(default_factory=ToolSafetyPolicy)


class ToolContractMapResponse(BaseModel):
    version: str
    route: str = "tool_contract_map_metadata_only"
    contracts: list[ToolContractSpec] = Field(default_factory=list)
    metadata_only: bool = True
    execution_enabled: bool = False
    workbook_read: bool = False
    engine_called: bool = False
    excel_created: bool = False
    legacy_builder_called: bool = False
    tool_execution_called: bool = False
