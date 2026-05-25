from __future__ import annotations

import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from jarvis_v5.parsers.alias_parser import parse_alias_edit
from jarvis_v5.parsers.conflict_guard import detect_setup_conflict, plan_normalization_report
from jarvis_v5.parsers.heading_parser import parse_heading_assignments
from jarvis_v5.parsers.level_parser import parse_levels
from jarvis_v5.parsers.trade_parser import parse_trade_function_unit
from jarvis_v5.registry.trade_profile_registry import clean_trade_registry_payload
from jarvis_v5.parsers.zone_parser import parse_zone_edit, parse_zone_set_edits
from jarvis_v5.reducers.level_reducer import set_levels
from jarvis_v5.reducers.trade_reducer import apply_trade_function_unit_changes
from jarvis_v5.tools.builder.function_unit_compatibility import compatibility_conflict_payload, validate_function_unit_compatibility
from jarvis_v5.reducers.zone_reducer import append_zone_values, find_zones_containing, replace_zone_value, set_zone
from jarvis_v5.schemas.builder_plan_schema import ensure_builder_shell_plan
from jarvis_v5.schemas.reducer_schema import ReducerResult
from jarvis_v5.reducers.setup_text_normalizer import normalize_active_setup_text


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _zone_replace_clarification(old_value: str, new_value: str, zone_ids: list[int]) -> dict[str, Any]:
    return {
        "clarification_id": f"clar_{uuid.uuid4().hex}",
        "type": "zone_replace_confirmation",
        "prompt": f"Do you want to replace {old_value} with {new_value}, or add {new_value} as a new Zone value?",
        "options": ["Confirm replace", "Add as new", "Cancel"],
        "expected_answer_classes": ["replace", "add", "cancel"],
        "resolver_name": "resolve_zone_replace_confirmation",
        "context": {"old_value": old_value, "new_value": new_value, "zone_ids": zone_ids},
        "repeats": 0,
        "max_repeats": 2,
        "status": "open",
        "created_at": _now(),
        "updated_at": _now(),
    }



def _sync_zone_heading_assignments(plan: dict[str, Any]) -> None:
    assignments = plan.setdefault("heading_assignments", {})
    for zone in plan.setdefault("dynamic_zones", []):
        zone_id = str(zone.get("zone_id"))
        if zone_id in assignments:
            zone["head_assignment"] = assignments[zone_id]


def _apply_heading_assignments(plan: dict[str, Any], parsed: dict[str, Any]) -> list[str]:
    changed: list[str] = []
    assignments = parsed.get("assignments") or {}
    if assignments:
        target = plan.setdefault("heading_assignments", {})
        for zone_id, head in assignments.items():
            if target.get(str(zone_id)) != head:
                target[str(zone_id)] = head
                changed.append("heading_assignments")
        _sync_zone_heading_assignments(plan)
    if parsed.get("start_head"):
        plan.setdefault("item_code_settings", {})["start_head"] = parsed["start_head"]
        changed.append("item_code_settings")
    return sorted(set(changed))


def _apply_alias_edit(plan: dict[str, Any], parsed: dict[str, Any]) -> list[str]:
    aliases = plan.setdefault("aliases", {})
    if parsed.get("action") == "set":
        aliases.update(parsed.get("aliases") or {})
        return ["aliases"]
    if parsed.get("action") == "replace":
        old = str(parsed.get("old") or "")
        new = str(parsed.get("new") or "")
        # Prefer updating existing alias pairs, but safely store an explicit alias if none exists.
        updated = False
        for key, value in list(aliases.items()):
            if key.lower() == old.lower():
                aliases[new] = aliases.pop(key)
                updated = True
            elif str(value).lower() == old.lower():
                aliases[key] = new
                updated = True
        if not updated and old and new:
            aliases[new] = old
        return ["aliases"]
    return []




def _clean_conflict_payload(conflict: dict[str, Any]) -> dict[str, Any]:
    return {
        "conflict_type": conflict.get("conflict_type"),
        "conflicting_slots": conflict.get("conflicting_slots") or [],
        "options": conflict.get("options") or [],
        "message": conflict.get("message"),
        "trade_registry": clean_trade_registry_payload(conflict.get("trade_registry")),
    }


def _normalization_payload(plan: dict[str, Any] | None, text_normalization=None, *, conflicts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    report = plan_normalization_report(plan, conflicts=conflicts)
    if text_normalization is not None:
        norm_payload = text_normalization.as_dict()
        report.update(norm_payload)
    if conflicts:
        report["conflicts"] = [_clean_conflict_payload(conflict) for conflict in conflicts]
    return report


def _split_setup_clauses_for_reducer(text: str) -> list[str]:
    import re
    parts = re.split(r"(?:\n+|;|(?<=\.)\s+)", text or "")
    return [part.strip() for part in parts if part and part.strip()] or [(text or "").strip()]

def _conflict_result(conflict: dict[str, Any], text_normalization=None) -> ReducerResult:
    conflicts = [conflict]
    return ReducerResult(
        handled=True,
        action="conflict_guard",
        slot="setup",
        changes={},
        requires_clarification=True,
        clarification=conflict.get("clarification"),
        message=conflict.get("message") or "Builder setup needs clarification before I update the plan.",
        warnings=["setup_conflict_guard"],
        changed_slots=[],
        confidence=0.88,
        conflict_type=conflict.get("conflict_type"),
        conflicting_slots=conflict.get("conflicting_slots") or [],
        options=conflict.get("options") or [],
        conflicts=[_clean_conflict_payload(conflict)],
        plan_mutated=False,
        normalization=_normalization_payload(None, text_normalization, conflicts=conflicts),
        trade_registry=clean_trade_registry_payload(conflict.get("trade_registry")),
    )


def _apply_single_zone_head_if_safe(plan: dict[str, Any], text: str) -> tuple[bool, ReducerResult | None]:
    import re
    m = re.search(r"\b(?:use|set|change)?\s*head\s*([1-4])\b", text, flags=re.I)
    if not m or re.search(r"\bzone\s*\d+\b", text, flags=re.I):
        return False, None
    zones = [zone for zone in plan.get("dynamic_zones", []) or [] if zone.get("zone_id") is not None]
    if len(zones) != 1:
        return False, None
    zone_id = int(zones[0]["zone_id"])
    head = f"Head{int(m.group(1))}"
    plan.setdefault("heading_assignments", {})[str(zone_id)] = head
    _sync_zone_heading_assignments(plan)
    return True, ReducerResult(
        handled=True, action="set", slot="heading_assignments",
        changes={"assignments": {str(zone_id): head}},
        message=f"Done — set Zone {zone_id} to {head}.",
        confidence=0.9, changed_slots=["heading_assignments"],
        plan_mutated=True, normalization=plan_normalization_report(plan),
    )

def _apply_slot_edit_single(plan: dict[str, Any] | None, text: str) -> tuple[dict[str, Any], ReducerResult]:
    plan = ensure_builder_shell_plan(plan)
    stripped = text.strip()
    if not stripped:
        return plan, ReducerResult(handled=False, message="No edit text supplied.", changed_slots=[])

    # Conflict guards must see both raw text and normalized/canonical text so
    # natural phrasing cannot hide function/unit or trade conflicts.
    raw_conflict = detect_setup_conflict(plan, stripped)
    if raw_conflict:
        return plan, _conflict_result(raw_conflict)

    text_normalization = normalize_active_setup_text(stripped)
    edit_text = text_normalization.canonical_text
    if text_normalization.applied and edit_text != stripped:
        canonical_conflict = detect_setup_conflict(plan, edit_text)
        if canonical_conflict:
            return plan, _conflict_result(canonical_conflict, text_normalization)
    else:
        edit_text = stripped

    single_head_applied, single_head_result = _apply_single_zone_head_if_safe(plan, edit_text)
    if single_head_applied and single_head_result:
        return plan, single_head_result

    # Alias edits that mention Mezz/Mezzanine must be handled before the
    # generic "Change X to Y" zone replacement parser.
    alias = parse_alias_edit(edit_text)
    if alias:
        changed = _apply_alias_edit(plan, alias)
        return plan, ReducerResult(
            handled=True, action=alias.get("action"), slot="aliases", changes=alias,
            message="Done — updated aliases.",
            confidence=alias.get("confidence", 0.85), changed_slots=changed or ["aliases"], plan_mutated=True, normalization=_normalization_payload(plan, text_normalization),
        )

    zone_sets = parse_zone_set_edits(edit_text)
    if len(zone_sets) > 1:
        changed_zone_ids: list[int] = []
        for zone_set in zone_sets:
            set_zone(plan, zone_set["zone_id"], zone_set["values"])
            changed_zone_ids.append(zone_set["zone_id"])
        _sync_zone_heading_assignments(plan)
        plan["confidence"] = max(float(plan.get("confidence") or 0), 0.95)
        return plan, ReducerResult(
            handled=True, action="set", slot="zones",
            changes={"zones": [{"zone_id": z["zone_id"], "values": z["values"]} for z in zone_sets]},
            message="Done — set " + "; ".join(f"Zone {z['zone_id']} to {', '.join(z['values'])}" for z in zone_sets) + ".",
            confidence=0.95, changed_slots=["dynamic_zones"], plan_mutated=True, normalization=_normalization_payload(plan, text_normalization),
        )

    zone = parse_zone_edit(edit_text)
    if zone:
        action = zone["action"]
        if action == "set":
            set_zone(plan, zone["zone_id"], zone["values"])
            _sync_zone_heading_assignments(plan)
            plan["confidence"] = max(float(plan.get("confidence") or 0), zone.get("confidence", 0.0))
            return plan, ReducerResult(
                handled=True, action="set", slot="zones",
                changes={"zone_id": zone["zone_id"], "values": zone["values"]},
                message=f"Done — set Zone {zone['zone_id']} to {', '.join(zone['values'])}.",
                confidence=zone.get("confidence", 0.95), changed_slots=["dynamic_zones"], plan_mutated=True, normalization=_normalization_payload(plan, text_normalization),
            )
        if action == "append":
            append_zone_values(plan, zone["zone_id"], zone["values"])
            _sync_zone_heading_assignments(plan)
            return plan, ReducerResult(
                handled=True, action="append", slot="zones",
                changes={"zone_id": zone["zone_id"], "values": zone["values"]},
                message=f"Done — added {', '.join(zone['values'])} to Zone {zone['zone_id']}.",
                confidence=zone.get("confidence", 0.9), changed_slots=["dynamic_zones"], plan_mutated=True, normalization=_normalization_payload(plan, text_normalization),
            )
        if action == "replace":
            ok = replace_zone_value(plan, zone["zone_id"], zone["old_value"], zone["new_value"])
            if not ok:
                return plan, ReducerResult(
                    handled=True, action="replace_failed", slot="zones",
                    changes={"zone_id": zone["zone_id"], "old_value": zone["old_value"], "new_value": zone["new_value"]},
                    message=f"I could not replace {zone['old_value']} in Zone {zone['zone_id']} because it is not in the current plan.",
                    warnings=["replace_target_missing"], confidence=0.8, changed_slots=[], plan_mutated=False, normalization=_normalization_payload(plan, text_normalization),
                )
            return plan, ReducerResult(
                handled=True, action="replace", slot="zones",
                changes={"zone_id": zone["zone_id"], "old_value": zone["old_value"], "new_value": zone["new_value"]},
                message=f"Done — replaced Zone {zone['zone_id']}: {zone['old_value']} with {zone['new_value']}.",
                confidence=zone.get("confidence", 0.9), changed_slots=["dynamic_zones"], plan_mutated=True, normalization=_normalization_payload(plan, text_normalization),
            )
        if action == "ambiguous_replace":
            matches = find_zones_containing(plan, zone["old_value"])
            clarification = _zone_replace_clarification(zone["old_value"], zone["new_value"], matches)
            return plan, ReducerResult(
                handled=True, action="ambiguous_replace", slot="zones",
                changes={"old_value": zone["old_value"], "new_value": zone["new_value"], "matching_zone_ids": matches},
                requires_clarification=True, clarification=clarification, message=clarification["prompt"],
                confidence=zone.get("confidence", 0.75), changed_slots=[], plan_mutated=False, normalization=_normalization_payload(plan, text_normalization),
            )

    heading = parse_heading_assignments(edit_text)
    if heading:
        changed = _apply_heading_assignments(plan, heading)
        return plan, ReducerResult(
            handled=True, action="set", slot="heading_assignments", changes=heading,
            message="Done — updated heading assignments.",
            confidence=heading.get("confidence", 0.9), changed_slots=changed or ["heading_assignments"], plan_mutated=bool(changed), normalization=_normalization_payload(plan, text_normalization),
        )

    levels = parse_levels(edit_text)
    if levels:
        set_levels(plan, levels["levels"])
        return plan, ReducerResult(
            handled=True, action="set", slot="levels", changes={"levels": levels["levels"]},
            message="Done — set Levels to " + ", ".join(levels["levels"]) + ".",
            confidence=levels.get("confidence", 0.9), changed_slots=["levels"], plan_mutated=True, normalization=_normalization_payload(plan, text_normalization),
        )

    trade = parse_trade_function_unit(edit_text)
    if trade:
        candidate_plan = deepcopy(plan)
        apply_trade_function_unit_changes(candidate_plan, trade["changes"])
        compat = validate_function_unit_compatibility(
            costx_function=candidate_plan.get("costx_function"),
            unit=candidate_plan.get("unit"),
            trade_profile=candidate_plan.get("trade_profile"),
            custom_quantity=candidate_plan.get("custom_quantity"),
        )
        if compat.get("checked") and not compat.get("valid"):
            return plan, _conflict_result(compatibility_conflict_payload(compat), text_normalization)
        apply_trade_function_unit_changes(plan, trade["changes"])
        changed_slots = [key for key in trade["changes"].keys() if key != "trade_registry"]
        return plan, ReducerResult(
            handled=True, action="set", slot="trade_function_unit", changes=trade["changes"],
            message="Done — updated " + ", ".join(trade.get("message_parts") or changed_slots or trade["changes"].keys()) + ".",
            confidence=trade.get("confidence", 0.9), changed_slots=changed_slots, plan_mutated=True, normalization=_normalization_payload(plan, text_normalization),
            trade_registry=trade.get("trade_registry"),
        )

    return plan, ReducerResult(
        handled=False, message="I kept the current setup unchanged. This edit is not supported yet in alpha.3.1.",
        confidence=0.0, changed_slots=[], plan_mutated=False, normalization=_normalization_payload(plan, text_normalization),
    )


def _apply_multi_slot_edit(
    plan: dict[str, Any],
    edit_text: str,
    text_normalization,
) -> tuple[dict[str, Any], ReducerResult] | None:
    clauses = _split_setup_clauses_for_reducer(edit_text)
    candidate_plan = deepcopy(plan)
    changed_slots: list[str] = []
    changes: dict[str, Any] = {}
    message_parts: list[str] = []
    confidence = 0.0
    edit_group_count = 0
    trade_registry_payload: dict[str, Any] | None = None

    # Trade/function/unit may span the full message, so parse the canonical text as a whole.
    trade = parse_trade_function_unit(edit_text)
    if trade:
        apply_trade_function_unit_changes(candidate_plan, trade["changes"])
        compat = validate_function_unit_compatibility(
            costx_function=candidate_plan.get("costx_function"),
            unit=candidate_plan.get("unit"),
            trade_profile=candidate_plan.get("trade_profile"),
            custom_quantity=candidate_plan.get("custom_quantity"),
        )
        if compat.get("checked") and not compat.get("valid"):
            return plan, _conflict_result(compatibility_conflict_payload(compat), text_normalization)
        changed = [key for key in trade["changes"].keys() if key != "trade_registry"]
        if changed:
            changes.update({key: value for key, value in trade["changes"].items() if key != "trade_registry"})
            changes["trade_function_unit"] = trade["changes"]
            changed_slots.extend(changed)
            message_parts.extend(trade.get("message_parts") or changed)
            confidence = max(confidence, float(trade.get("confidence") or 0.9))
            edit_group_count += 1
            trade_registry_payload = trade.get("trade_registry")

    zone_changes: list[dict[str, Any]] = []
    for clause in clauses:
        zone_sets = parse_zone_set_edits(clause)
        if zone_sets:
            for zone_set in zone_sets:
                set_zone(candidate_plan, zone_set["zone_id"], zone_set["values"])
                zone_changes.append({"zone_id": zone_set["zone_id"], "values": zone_set["values"]})
            continue
        zone = parse_zone_edit(clause)
        if zone and zone.get("action") == "set":
            set_zone(candidate_plan, zone["zone_id"], zone["values"])
            zone_changes.append({"zone_id": zone["zone_id"], "values": zone["values"]})
    if zone_changes:
        _sync_zone_heading_assignments(candidate_plan)
        candidate_plan["confidence"] = max(float(candidate_plan.get("confidence") or 0), 0.95)
        changes["zones"] = zone_changes
        changed_slots.append("dynamic_zones")
        message_parts.append("zones")
        confidence = max(confidence, 0.95)
        edit_group_count += 1

    heading_changes: list[dict[str, Any]] = []
    for clause in clauses:
        heading = parse_heading_assignments(clause)
        if heading:
            changed = _apply_heading_assignments(candidate_plan, heading)
            if changed:
                heading_changes.append(heading)
    if not heading_changes:
        for clause in clauses:
            single_ok, single_result = _apply_single_zone_head_if_safe(candidate_plan, clause)
            if single_ok and single_result:
                heading_changes.append(single_result.changes)
                break
    if heading_changes:
        changes["heading_assignments"] = heading_changes
        changed_slots.append("heading_assignments")
        message_parts.append("heading assignments")
        confidence = max(confidence, 0.92)
        edit_group_count += 1

    levels_parsed = None
    for clause in clauses + [edit_text]:
        levels = parse_levels(clause)
        if levels:
            levels_parsed = levels
            break
    if levels_parsed:
        set_levels(candidate_plan, levels_parsed["levels"])
        changes["levels"] = {"levels": levels_parsed["levels"]}
        changed_slots.append("levels")
        message_parts.append("levels")
        confidence = max(confidence, float(levels_parsed.get("confidence") or 0.9))
        edit_group_count += 1

    # Alias edits stay independent and are safe to combine with setup clauses.
    alias = parse_alias_edit(edit_text)
    if alias:
        changed = _apply_alias_edit(candidate_plan, alias)
        if changed:
            changes["aliases"] = alias
            changed_slots.extend(changed)
            message_parts.append("aliases")
            confidence = max(confidence, float(alias.get("confidence") or 0.85))
            edit_group_count += 1

    unique_changed_slots = sorted(dict.fromkeys(changed_slots))
    # Let the single-slot path handle simple single edits. Multi-slot is for
    # combined setup messages or trade/function/unit messages that set multiple slots.
    if edit_group_count < 2 and len(unique_changed_slots) < 2:
        return None

    compat = validate_function_unit_compatibility(
        costx_function=candidate_plan.get("costx_function"),
        unit=candidate_plan.get("unit"),
        trade_profile=candidate_plan.get("trade_profile"),
        custom_quantity=candidate_plan.get("custom_quantity"),
    )
    if compat.get("checked") and not compat.get("valid"):
        return plan, _conflict_result(compatibility_conflict_payload(compat), text_normalization)

    plan.clear()
    plan.update(candidate_plan)
    normalization = _normalization_payload(plan, text_normalization)
    return plan, ReducerResult(
        handled=True,
        action="set",
        slot="multi_setup",
        changes=changes,
        message="Done — updated " + ", ".join(dict.fromkeys(message_parts or unique_changed_slots)) + ".",
        confidence=confidence or 0.9,
        changed_slots=unique_changed_slots,
        plan_mutated=True,
        normalization=normalization,
        trade_registry=trade_registry_payload,
    )



def looks_like_slot_edit_text(plan: dict[str, Any] | None, text: str) -> bool:
    plan = ensure_builder_shell_plan(plan)
    stripped = (text or "").strip()
    if not stripped:
        return False
    text_normalization = normalize_active_setup_text(stripped)
    canonical = text_normalization.canonical_text if text_normalization.applied else stripped
    if detect_setup_conflict(plan, stripped) or (canonical != stripped and detect_setup_conflict(plan, canonical)):
        return True
    if parse_trade_function_unit(canonical):
        return True
    if parse_zone_set_edits(canonical) or parse_zone_edit(canonical):
        return True
    if parse_heading_assignments(canonical) or parse_levels(canonical) or parse_alias_edit(canonical):
        return True
    for clause in _split_setup_clauses_for_reducer(canonical):
        if parse_trade_function_unit(clause) or parse_zone_set_edits(clause) or parse_zone_edit(clause) or parse_heading_assignments(clause) or parse_levels(clause) or parse_alias_edit(clause):
            return True
        ok, _result = _apply_single_zone_head_if_safe(deepcopy(plan), clause)
        if ok:
            return True
    return False


def apply_slot_edit(plan: dict[str, Any] | None, text: str) -> tuple[dict[str, Any], ReducerResult]:
    plan = ensure_builder_shell_plan(plan)
    stripped = text.strip()
    if not stripped:
        return plan, ReducerResult(handled=False, message="No edit text supplied.", changed_slots=[])

    text_normalization = normalize_active_setup_text(stripped)
    raw_conflict = detect_setup_conflict(plan, stripped)
    if raw_conflict:
        return plan, _conflict_result(raw_conflict, text_normalization)

    edit_text = text_normalization.canonical_text if text_normalization.applied else stripped
    if text_normalization.applied and edit_text != stripped:
        canonical_conflict = detect_setup_conflict(plan, edit_text)
        if canonical_conflict:
            return plan, _conflict_result(canonical_conflict, text_normalization)

    multi_result = _apply_multi_slot_edit(plan, edit_text, text_normalization)
    if multi_result is not None:
        return multi_result

    return _apply_slot_edit_single(plan, stripped)


def resolve_zone_replace_confirmation(plan: dict[str, Any] | None, clarification: dict[str, Any], answer_text: str) -> tuple[dict[str, Any], ReducerResult]:
    from jarvis_v5.router.action_aliases import normalize_text

    plan = ensure_builder_shell_plan(plan)
    normalized = normalize_text(answer_text)
    context = clarification.get("context") or {}
    old_value = context.get("old_value")
    new_value = context.get("new_value")
    zone_ids = context.get("zone_ids") or []

    if normalized in {"confirm replace", "replace", "yes replace", "confirm"}:
        if not zone_ids:
            return plan, ReducerResult(
                handled=True, action="replace_failed", slot="zones", changes={"old_value": old_value, "new_value": new_value},
                message=f"I cannot replace {old_value} because it is not in the current Zone plan.",
                warnings=["replace_target_missing"], confidence=0.8, changed_slots=[], plan_mutated=False, normalization=plan_normalization_report(plan),
            )
        changed: list[int] = []
        for zone_id in zone_ids:
            if replace_zone_value(plan, int(zone_id), old_value, new_value):
                changed.append(int(zone_id))
        if not changed:
            return plan, ReducerResult(
                handled=True, action="replace_failed", slot="zones", changes={"old_value": old_value, "new_value": new_value},
                message=f"I cannot replace {old_value} because it is not in the current Zone plan.",
                warnings=["replace_target_missing"], confidence=0.8, changed_slots=[], plan_mutated=False, normalization=plan_normalization_report(plan),
            )
        return plan, ReducerResult(
            handled=True, action="replace_confirmed", slot="zones",
            changes={"zone_ids": changed, "old_value": old_value, "new_value": new_value},
            message=f"Done — replaced {old_value} with {new_value} in Zone {', '.join(str(z) for z in changed)}.",
            confidence=0.9, changed_slots=["dynamic_zones"], plan_mutated=True, normalization=plan_normalization_report(plan),
        )

    if normalized in {"add as new", "add", "add new", "add as new value"}:
        target_ids = zone_ids or [1]
        for zone_id in target_ids:
            append_zone_values(plan, int(zone_id), [new_value])
        return plan, ReducerResult(
            handled=True, action="append", slot="zones", changes={"zone_ids": target_ids, "values": [new_value]},
            message=f"Done — added {new_value} as a new Zone value.", confidence=0.85, changed_slots=["dynamic_zones"], plan_mutated=True, normalization=plan_normalization_report(plan),
        )

    if normalized in {"cancel", "cancel clarification"}:
        return plan, ReducerResult(
            handled=True, action="cancelled", slot="zones",
            message="Clarification cancelled. The active Builder plan was not changed.", confidence=0.9, changed_slots=[], plan_mutated=False, normalization=plan_normalization_report(plan),
        )

    return plan, ReducerResult(handled=False, message=clarification.get("prompt") or "Please answer the clarification.", changed_slots=[])
