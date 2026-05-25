from __future__ import annotations

import re
from typing import Any


def _level_label(raw: str) -> str:
    raw = raw.strip().lower()
    if raw in {"gf", "ground floor"}:
        return "GF"
    if raw == "podium":
        return "Podium"
    m = re.search(r"(?:basement|b)\s*(\d+)", raw, flags=re.I)
    if m:
        return f"B{int(m.group(1))}"
    m = re.search(r"(?:l|level|lvl)\s*(\d+)", raw, flags=re.I)
    if m:
        return f"L{int(m.group(1))}"
    return raw.upper()


def _range(start: str, end: str) -> list[str]:
    start = _level_label(start)
    end = _level_label(end)
    if start == "GF" and end.startswith("L"):
        return ["GF"] + [f"L{i}" for i in range(1, int(end[1:]) + 1)]
    if start.startswith("L") and end.startswith("L"):
        a, b = int(start[1:]), int(end[1:])
        step = 1 if b >= a else -1
        return [f"L{i}" for i in range(a, b + step, step)]
    if start.startswith("B") and end.startswith("B"):
        a, b = int(start[1:]), int(end[1:])
        step = -1 if a >= b else 1
        return [f"B{i}" for i in range(a, b + step, step)]
    if start.startswith("B") and end == "GF":
        a = int(start[1:])
        return [f"B{i}" for i in range(a, 0, -1)] + ["GF"]
    return [start, end]


def _append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def parse_levels(text: str) -> dict[str, Any] | None:
    if not text.strip():
        return None
    lower = text.lower()
    if not ("level" in lower or "levels" in lower or "mezz" in lower or "podium" in lower or re.search(r"\bgf\s+to\s+(?:l|level)\s*\d+\b", lower) or re.search(r"\bb\s*\d+\s+to\s+b\s*\d+\b", lower)):
        return None

    levels: list[str] = []

    # Ranges: GF to L3, B2 to B1, L1 to L10, GF to Level 11
    range_pattern = r"(b\s*\d+|basement\s*\d+|gf|ground floor|podium|l\s*\d+|level\s*\d+|lvl\s*\d+)\s+to\s+(b\s*\d+|basement\s*\d+|gf|ground floor|podium|l\s*\d+|level\s*\d+|lvl\s*\d+)"
    for start, end in re.findall(range_pattern, text, flags=re.I):
        for level in _range(start, end):
            _append_unique(levels, level)

    # Explicit level tokens in list-style command. Ignore ones already covered.
    for token in re.findall(r"\b(?:gf|ground floor|podium|b\s*\d+|basement\s*\d+|l\s*\d+|level\s*\d+|lvl\s*\d+)\b", text, flags=re.I):
        _append_unique(levels, _level_label(token))

    # Mezzanine on L1, L2, and L5
    mezz_match = re.search(r"\b(?:mezz|mezzanine)\s+(?:on|at|for)\s+(.+?)(?:$|[.;])", text, flags=re.I)
    if mezz_match:
        for num in re.findall(r"(?:L|Level|Lvl)\s*(\d+)", mezz_match.group(1), flags=re.I):
            _append_unique(levels, f"L{int(num)} Mezzanine")

    # with Level 11 Mezzanine / L11 Mezzanine
    for num in re.findall(r"\b(?:level|l|lvl)\s*(\d+)\s+(?:mezz|mezzanine)\b", text, flags=re.I):
        _append_unique(levels, f"L{int(num)} Mezzanine")

    # Exclusions: excluding L3 and L4 / exclude L3, L4
    exclusions: set[str] = set()
    ex_match = re.search(r"\bexclud(?:e|ing)\s+(.+)$", text, flags=re.I)
    if ex_match:
        for token in re.findall(r"\b(?:b\s*\d+|basement\s*\d+|gf|ground floor|podium|l\s*\d+|level\s*\d+|lvl\s*\d+)\b", ex_match.group(1), flags=re.I):
            exclusions.add(_level_label(token))
    if exclusions:
        levels = [level for level in levels if level not in exclusions]

    if not levels:
        return None
    return {"action": "set", "levels": levels, "confidence": 0.9}
