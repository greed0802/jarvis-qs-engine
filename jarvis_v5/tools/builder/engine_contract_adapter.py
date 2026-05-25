from __future__ import annotations

from typing import Any
from jarvis_v5.schemas.builder_adapter_schema import BuilderAdapterDryRunResult
from jarvis_v5.schemas.builder_snapshot_schema import BuilderRunSnapshot
from jarvis_v5.schemas.builder_engine_contract_schema import (
    BuilderEngineContract,
    BuilderEngineContractBlocker,
    BuilderEngineContractValidation,
    BuilderEngineSetupContract,
    compute_contract_hash,
    new_contract_id,
)


def _setup_ready(setup: dict[str, Any] | None) -> bool:
    return bool(setup and setup.get("ready_for_future_engine") is True)


def _blocker(code: str, message: str, fields: list[str] | None = None) -> BuilderEngineContractBlocker:
    return BuilderEngineContractBlocker(code=code, message=message, fields=fields or [])


def _missing_fields_from_setup(setup: dict[str, Any] | None) -> list[str]:
    return list((setup or {}).get("missing_required") or [])


def validate_contract_sources(*, snapshot: BuilderRunSnapshot, adapter: BuilderAdapterDryRunResult | None = None) -> BuilderEngineContractValidation:
    """Validate the alpha.11 contract safety boundary.

    Alpha.11 deliberately requires a current adapter dry run. This keeps the
    future engine boundary deterministic: contract payloads come from the same
    normalized adapter input every time, never directly from workbook parsing or
    a partially normalized snapshot path.
    """
    issues: list[str] = []
    warnings: list[str] = []
    blockers: list[BuilderEngineContractBlocker] = []

    def add(code: str, message: str, fields: list[str] | None = None) -> None:
        if code not in issues:
            issues.append(code)
            blockers.append(_blocker(code, message, fields))

    setup = snapshot.setup_completeness or {}
    missing = _missing_fields_from_setup(setup)

    if snapshot.status != "current":
        add("snapshot_is_stale", "Builder snapshot is stale. Create a new snapshot from the current plan.")
    if not snapshot.workbook_ref:
        add("missing_workbook_ref", "Workbook metadata is missing from the Builder snapshot.", ["workbook_ref"])
    if not snapshot.trade_profile:
        add("missing_trade_profile", "Trade/profile is missing from the Builder snapshot.", ["trade_profile"])
    if not snapshot.costx_function:
        add("missing_costx_function", "CostX function is missing from the Builder snapshot.", ["costx_function"])
    if not snapshot.unit:
        add("missing_unit", "Unit is missing from the Builder snapshot.", ["unit"])
    if snapshot.costx_function == "XGETCUSTOM" and not snapshot.custom_quantity:
        add("missing_custom_quantity", "Custom quantity is required for XGETCUSTOM.", ["custom_quantity"])
    if snapshot.zone_mode == "rebuild" and not snapshot.dynamic_zones:
        add("missing_dynamic_zones", "Dynamic zones are required for rebuild mode.", ["dynamic_zones"])
    if snapshot.zone_mode == "rebuild" and not snapshot.heading_assignments:
        add("missing_heading_assignments", "Heading assignments are required for rebuild mode.", ["heading_assignments"])
    if not snapshot.levels:
        add("missing_levels", "Levels are missing from the Builder snapshot.", ["levels"])
    if snapshot.conflicts:
        add("setup_conflict_unresolved", "Unresolved setup conflicts are present.", ["conflicts"])
    normalization = snapshot.normalization or {}
    if normalization.get("status") == "needs_clarification":
        add("normalization_needs_clarification", "Setup normalization still needs clarification.", ["normalization"])
    if not _setup_ready(setup):
        add("setup_not_ready_for_future_engine", "Builder setup is not ready for future engine connection.", missing)

    if adapter is None:
        add("adapter_required", "A current Builder adapter dry run is required before creating an engine contract.", ["adapter_input_id"])
    else:
        if adapter.snapshot_id != snapshot.snapshot_id:
            add("adapter_is_stale", "Adapter dry run was created from a different snapshot.", ["adapter_input_id", "snapshot_id"])
        if adapter.freshness != "current":
            add("adapter_is_stale", "Adapter dry run is stale. Run adapter dry run again.", ["adapter_input_id"])
        if adapter.blocked:
            add("adapter_blocked", "Adapter dry run is blocked.", ["adapter_input_id"])
        if not adapter.validation.valid_for_future_engine:
            add("adapter_not_ready_for_future_engine", "Adapter dry run is not ready for future engine connection.", ["adapter_input_id"])
        if adapter.engine_called:
            add("adapter_engine_called_unexpectedly", "Adapter safety violation: engine_called was true.", ["engine_called"])
        if adapter.excel_created:
            add("adapter_excel_created_unexpectedly", "Adapter safety violation: excel_created was true.", ["excel_created"])
        if getattr(adapter, "workbook_read", False):
            add("adapter_workbook_read_unexpectedly", "Adapter safety violation: workbook_read was true.", ["workbook_read"])

    return BuilderEngineContractValidation(valid=not issues, blockers=blockers, issues=issues, warnings=warnings)


def create_builder_engine_contract(*, snapshot: BuilderRunSnapshot, adapter: BuilderAdapterDryRunResult | None = None) -> BuilderEngineContract:
    validation = validate_contract_sources(snapshot=snapshot, adapter=adapter)
    contract = BuilderEngineContract(
        contract_id=new_contract_id(),
        conversation_id=snapshot.conversation_id,
        task_id=snapshot.task_id,
        snapshot_id=snapshot.snapshot_id,
        adapter_input_id=adapter.adapter_input_id if adapter else None,
        source="builder_adapter_input" if adapter else "builder_run_snapshot",
        contract_status="ready_for_engine_connection" if validation.valid else "blocked",
        workbook_ref=snapshot.workbook_ref or {},
        builder_setup=BuilderEngineSetupContract(
            trade_profile=snapshot.trade_profile,
            costx_function=snapshot.costx_function,
            custom_quantity=snapshot.custom_quantity,
            unit=snapshot.unit,
            zone_mode=snapshot.zone_mode,
            dynamic_zones=snapshot.dynamic_zones,
            heading_assignments=snapshot.heading_assignments,
            levels=snapshot.levels,
            aliases=snapshot.aliases,
            item_code_settings=snapshot.item_code_settings,
            trade_registry=getattr(snapshot, "trade_registry", None),
        ),
        setup_completeness=snapshot.setup_completeness,
        normalization=snapshot.normalization,
        conflicts=snapshot.conflicts,
        validation=validation,
    )
    contract.contract_hash = compute_contract_hash(contract)
    return contract


def contract_trace_payload(contract: BuilderEngineContract | None) -> dict[str, Any] | None:
    if not contract:
        return None
    return {
        "found": True,
        "contract_id": contract.contract_id,
        "status": contract.contract_status,
        "snapshot_id": contract.snapshot_id,
        "adapter_input_id": contract.adapter_input_id,
        "contract_schema_version": contract.contract_schema_version,
        "legacy_target": contract.legacy_target,
        "contract_only": contract.safety.contract_only,
        "legacy_builder_called": contract.safety.legacy_builder_called,
        "workbook_read": contract.safety.workbook_read,
        "engine_called": contract.safety.engine_called,
        "excel_created": contract.safety.excel_created,
        "validation": contract.validation.model_dump(mode="json"),
        "replay_url": f"/api/builder/engine-contract/{contract.contract_id}",
    }
