from __future__ import annotations

from typing import Any

NO_ENGINE_SAFETY = {
    "workbook_read": False,
    "engine_called": False,
    "excel_created": False,
    "contract_only": True,
    "legacy_builder_called": False,
}

CURRENT_ALLOWED_OPERATIONS = [
    "metadata_probe_after_approval",
    "sheet_name_probe_after_approval",
]

CURRENT_BLOCKED_OPERATIONS = [
    "open_workbook_for_content",
    "read_cells",
    "read_formulas",
    "read_workbook_dimensions",
    "read_used_ranges",
    "read_styles",
    "read_tables",
    "read_comments",
    "parse_workbook_contents",
    "call_builder_engine",
    "call_legacy_builder",
    "create_excel",
    "upgrade_preview_readiness",
    "upgrade_export_readiness",
]

FUTURE_ACCESS_TIERS = [
    {
        "tier": 0,
        "name": "metadata_only",
        "status": "available_alpha35",
        "workbook_opened": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "workbook_read": False,
        "execution_enabled": False,
    },
    {
        "tier": 1,
        "name": "sheet_name_probe_only",
        "status": "not_enabled",
        "requires_separate_approval_gate": True,
        "workbook_opened": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "workbook_read": False,
        "execution_enabled": False,
    },
    {
        "tier": 2,
        "name": "future_structure_or_dimension_policy",
        "status": "not_enabled",
        "requires_separate_approval_gate": True,
        "workbook_opened": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "workbook_read": False,
        "execution_enabled": False,
    },
    {
        "tier": 3,
        "name": "future_limited_cell_range_read",
        "status": "not_enabled",
        "requires_bounded_range_and_limits": True,
        "workbook_opened": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "workbook_read": False,
        "execution_enabled": False,
    },
    {
        "tier": 4,
        "name": "future_formula_token_or_value_policy",
        "status": "not_enabled",
        "requires_formula_mode_decision": True,
        "workbook_opened": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "workbook_read": False,
        "execution_enabled": False,
    },
    {
        "tier": 5,
        "name": "future_preview_data_contract",
        "status": "not_enabled",
        "requires_prior_read_policy": True,
        "workbook_opened": False,
        "sheet_names_read": False,
        "cells_read": False,
        "formulas_read": False,
        "workbook_read": False,
        "execution_enabled": False,
    },
]

REQUIRED_FUTURE_APPROVAL_GATES = [
    "structure_probe_policy",
    "limited_cell_range_probe_policy",
    "formula_token_or_cached_value_policy",
    "preview_data_contract_policy",
]


def _policy_safety_payload(**overrides: Any) -> dict[str, Any]:
    safety = {
        **dict(NO_ENGINE_SAFETY),
        "policy_only": True,
        "workbook_opened": False,
        "workbook_content_read": False,
        "workbook_parsed": False,
        "cells_read": False,
        "formulas_read": False,
        "dimension_read": False,
        "cell_read_enabled": False,
        "formula_read_enabled": False,
        "dimension_read_enabled": False,
        "workbook_parse_enabled": False,
        "preview_readiness_upgraded": False,
        "export_readiness_upgraded": False,
    }
    safety.update(overrides)
    return safety


def evaluate_workbook_read_policy_review(
    *,
    conversation_id: str,
    client_event_id: str | None = None,
) -> dict[str, Any]:
    """Return workbook-read policy metadata only.

    This alpha.35 owner defines future workbook access boundaries before any
    cell, formula, dimension, or content read is implemented. It never opens
    files, reads files, mutates Builder state, or upgrades preview/export
    readiness.
    """
    safety = _policy_safety_payload()
    blocked_by_policy = [
        "policy_review_only",
        "cell_read_disabled",
        "formula_read_disabled",
        "dimension_read_disabled",
        "workbook_parse_disabled",
        "execution_kill_switch",
    ]
    return {
        "conversation_id": conversation_id,
        "client_event_id": client_event_id,
        "route": "builder_workbook_read_policy_review",
        "message": "Workbook read policy reviewed. No workbook was opened and no cells, formulas, dimensions, Builder engine, or Excel output were used.",
        "policy_only": True,
        "current_access_tier": "sheet_name_probe_only",
        "current_allowed_operations": list(CURRENT_ALLOWED_OPERATIONS),
        "current_blocked_operations": list(CURRENT_BLOCKED_OPERATIONS),
        "future_access_tiers": list(FUTURE_ACCESS_TIERS),
        "required_future_approval_gates": list(REQUIRED_FUTURE_APPROVAL_GATES),
        "blocked_by_policy": blocked_by_policy,
        "cell_read_enabled": False,
        "formula_read_enabled": False,
        "dimension_read_enabled": False,
        "workbook_parse_enabled": False,
        "workbook_opened": False,
        "workbook_read": False,
        "workbook_content_read": False,
        "workbook_parsed": False,
        "cells_read": False,
        "formulas_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
        "preview_readiness_upgraded": False,
        "export_readiness_upgraded": False,
        "safety": safety,
        "readiness": {
            "status": "workbook_read_policy_reviewed",
            "preview_readiness_upgraded": False,
            "export_readiness_upgraded": False,
            "next_gate": "future_structure_probe_policy_review",
            "blocked_by_policy": blocked_by_policy,
        },
        "next_safe_action": "Review the workbook-read policy before any structure, cell, formula, or preview data probe is implemented.",
    }
