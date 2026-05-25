from __future__ import annotations

import re
from typing import Any

_LEVEL_TOKEN = r"(?:gf|ground floor|podium|b\s*\d+|basement\s*\d+|l\s*\d+|level\s*\d+|lvl\s*\d+)"
_RANGE_PATTERN = rf"({_LEVEL_TOKEN})\s+to\s+({_LEVEL_TOKEN})"
_EXPLICIT_LEVEL_PATTERN = rf"\b{_LEVEL_TOKEN}\b"
_EXCLUSION_PATTERN = r"\bexclud(?:e|ing)\s+(.+)$"
_MEZZANINE_ON_PATTERN = r"\b(?:mezz|mezzanine)\s+(?:on|at|for)\s+(.+?)(?:$|[.;])"
_MEZZANINE_LEVEL_PATTERN = r"(?:L|Level|Lvl)\s*(\d+)"
_MEZZANINE_TOKEN_PATTERN = r"\b(?:level|l|lvl)\s*(\d+)\s+(?:mezz|mezzanine)\b"


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
    start_label = _level_label(start)
    end_label = _level_label(end)

    if start_label == end_label:
        return [start_label]
    if start_label == "GF" and end_label.startswith("L"):
        return ["GF"] + [f"L{i}" for i in range(1, int(end_label[1:]) + 1)]
    if start_label.startswith("L") and end_label.startswith("L"):
        a, b = int(start_label[1:]), int(end_label[1:])
        step = 1 if b >= a else -1
        return [f"L{i}" for i in range(a, b + step, step)]
    if start_label.startswith("B") and end_label.startswith("B"):
        a, b = int(start_label[1:]), int(end_label[1:])
        step = -1 if a >= b else 1
        return [f"B{i}" for i in range(a, b + step, step)]
    if start_label.startswith("B") and end_label == "GF":
        a = int(start_label[1:])
        return [f"B{i}" for i in range(a, 0, -1)] + ["GF"]
    return [start_label, end_label]


def _append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def _parse_ranges(text: str, levels: list[str]) -> None:
    for start, end in re.findall(_RANGE_PATTERN, text, flags=re.I):
        for level in _range(start, end):
            _append_unique(levels, level)


def _parse_explicit_levels(text: str, levels: list[str]) -> None:
    for token in re.findall(_EXPLICIT_LEVEL_PATTERN, text, flags=re.I):
        _append_unique(levels, _level_label(token))


def _parse_mezzanine_levels(text: str, levels: list[str]) -> None:
    mezz_match = re.search(_MEZZANINE_ON_PATTERN, text, flags=re.I)
    if mezz_match:
        for num in re.findall(_MEZZANINE_LEVEL_PATTERN, mezz_match.group(1), flags=re.I):
            _append_unique(levels, f"L{int(num)} Mezzanine")
    for num in re.findall(_MEZZANINE_TOKEN_PATTERN, text, flags=re.I):
        _append_unique(levels, f"L{int(num)} Mezzanine")


def _parse_exclusions(text: str, levels: list[str]) -> None:
    ex_match = re.search(_EXCLUSION_PATTERN, text, flags=re.I)
    if not ex_match:
        return
    exclusions: set[str] = set()
    for token in re.findall(_EXPLICIT_LEVEL_PATTERN, ex_match.group(1), flags=re.I):
        exclusions.add(_level_label(token))
    if exclusions:
        levels[:] = [level for level in levels if level not in exclusions]


def parse_levels(text: str) -> dict[str, Any] | None:
    if not text.strip():
        return None

    lower = text.lower()
    if not (
        "level" in lower
        or "levels" in lower
        or "mezz" in lower
        or "podium" in lower
        or "basement" in lower
        or re.search(r"\bgf\s+to\s+(?:l|level)\s*\d+\b", lower)
        or re.search(r"\bb\s*\d+\s+to\s+b\s*\d+\b", lower)
    ):
        return None

    levels: list[str] = []
    _parse_ranges(text, levels)
    _parse_explicit_levels(text, levels)
    _parse_mezzanine_levels(text, levels)
    _parse_exclusions(text, levels)

    if not levels:
        return None

    return {"action": "set", "levels": levels, "confidence": 0.9}
