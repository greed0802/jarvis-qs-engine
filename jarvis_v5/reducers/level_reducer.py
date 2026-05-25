from __future__ import annotations


def set_levels(plan: dict, levels: list[str]) -> None:
    plan["levels"] = list(levels)
