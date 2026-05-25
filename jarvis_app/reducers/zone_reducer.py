from __future__ import annotations

from typing import Any


def get_zone(plan: dict[str, Any], zone_id: int) -> dict[str, Any] | None:
    for zone in plan.setdefault("dynamic_zones", []):
        if int(zone.get("zone_id")) == int(zone_id):
            return zone
    return None


def set_zone(plan: dict[str, Any], zone_id: int, values: list[str]) -> None:
    zone = get_zone(plan, zone_id)
    if zone is None:
        zone = {"zone_id": zone_id, "values": [], "head_assignment": None}
        plan.setdefault("dynamic_zones", []).append(zone)
    zone["values"] = list(values)


def append_zone_values(plan: dict[str, Any], zone_id: int, values: list[str]) -> None:
    zone = get_zone(plan, zone_id)
    if zone is None:
        zone = {"zone_id": zone_id, "values": [], "head_assignment": None}
        plan.setdefault("dynamic_zones", []).append(zone)
    existing = zone.setdefault("values", [])
    for value in values:
        if value not in existing:
            existing.append(value)


def replace_zone_value(plan: dict[str, Any], zone_id: int, old_value: str, new_value: str) -> bool:
    zone = get_zone(plan, zone_id)
    if not zone:
        return False
    values = zone.setdefault("values", [])
    for idx, value in enumerate(values):
        if value.lower() == old_value.lower():
            values[idx] = new_value
            return True
    return False


def find_zones_containing(plan: dict[str, Any], value: str) -> list[int]:
    matches: list[int] = []
    for zone in plan.get("dynamic_zones", []) or []:
        for existing in zone.get("values", []) or []:
            if existing.lower() == value.lower():
                matches.append(int(zone.get("zone_id")))
    return matches
