from __future__ import annotations

import re

from jarvis_v5.registry.trade_profile_registry import find_trade_registry_match
from jarvis_v5.router.action_aliases import normalize_text
from jarvis_v5.tools.builder.function_unit_compatibility import normalize_unit


TRADE_PATTERNS: list[tuple[str, str]] = [
    ("Wall Types", r"\b(?:wall\s*types?|walls?\s*/?\s*partitions?)\b"),
    ("Doors / Windows", r"\b(?:doors?\s*(?:and|/)?\s*windows?|windows?\s*(?:and|/)?\s*doors?)\b"),
    ("Structural Steel", r"\b(?:structural\s*steel|steel)\b"),
    ("Concrete / Reo", r"\b(?:concrete\s*/?\s*reo|structural\s*concrete|concrete)\b"),
]

FUNCTION_PATTERNS: list[tuple[str, str]] = [
    ("XGETCOUNT", r"\b(?:count|xgetcount)\b"),
    ("XGETWALLAREA", r"\b(?:wall\s*area|area\s+measurement|xgetwallarea)\b"),
    ("XGETCUSTOM", r"\bxgetcustom\b"),
]

CUSTOM_QUANTITY_PATTERNS: list[tuple[str, str, str]] = [
    ("Steel Surface Area", "XGETCUSTOM", r"\bsteel\s+surface\s+area\b"),
    ("Formworks", "XGETCUSTOM", r"\bformworks?\b"),
    ("Bar Reinforcement Weight", "XGETCUSTOM", r"\bbar\s+reinforcement\s+weight\b"),
    ("Reinforcement Weight", "XGETCUSTOM", r"\breinforcement\s+weight\b"),
]

UNIT_RE = re.compile(
    r"\bunit\s+(no|nr|count|item|each|pcs|m2|m²|m3|m³|lm|m|t|kg|sqm|sq\.?\s*m|(?:sq|square)\s+met(?:re|er)s?)\b"
    r"|\b(no|nr|count|item|each|pcs|m2|m²|m3|m³|lm|m|t|kg|sqm|sq\.?\s*m|(?:sq|square)\s+met(?:re|er)s?)\b",
    re.I,
)


def unique_signal_values(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return out


def _custom_quantity_patterns(*, include_weight_quantities: bool = True) -> list[tuple[str, str, str]]:
    if include_weight_quantities:
        return CUSTOM_QUANTITY_PATTERNS
    return [
        item
        for item in CUSTOM_QUANTITY_PATTERNS
        if item[0] not in {"Bar Reinforcement Weight", "Reinforcement Weight"}
    ]


def detect_trade_signals(text: str, *, include_registry: bool = False) -> list[str]:
    trades = [label for label, pattern in TRADE_PATTERNS if re.search(pattern, text, flags=re.I)]
    if include_registry:
        match = find_trade_registry_match(text)
        if match and not match.get("requires_clarification") and match.get("canonical_trade"):
            trades.append(str(match["canonical_trade"]))
    return unique_signal_values(trades)


def detect_function_signals(text: str, *, include_weight_quantities: bool = True) -> list[str]:
    funcs = [label for label, pattern in FUNCTION_PATTERNS if re.search(pattern, text, flags=re.I)]
    for _qty, function, pattern in _custom_quantity_patterns(include_weight_quantities=include_weight_quantities):
        if re.search(pattern, text, flags=re.I):
            funcs.append(function)
    return unique_signal_values(funcs)


def detect_custom_quantity_signals(text: str, *, include_weight_quantities: bool = True) -> list[str]:
    return unique_signal_values([
        qty
        for qty, _function, pattern in _custom_quantity_patterns(include_weight_quantities=include_weight_quantities)
        if re.search(pattern, text, flags=re.I)
    ])


def detect_unit_signals(
    text: str,
    *,
    include_weight_quantities: bool = True,
    prefer_explicit_units: bool = False,
) -> list[str]:
    explicit_units: list[str] = []
    bare_units: list[str] = []
    for match in UNIT_RE.finditer(text):
        explicit = match.group(1)
        bare = match.group(2)
        if explicit:
            explicit_units.append(normalize_unit(explicit) or explicit.lower())
        elif bare and (
            detect_function_signals(text, include_weight_quantities=include_weight_quantities)
            or detect_custom_quantity_signals(text, include_weight_quantities=include_weight_quantities)
        ):
            bare_units.append(normalize_unit(bare) or bare.lower())
    if prefer_explicit_units and explicit_units:
        return unique_signal_values(explicit_units)
    return unique_signal_values(explicit_units + bare_units)


def has_explicit_reinforcement_weight_t_setup(text: str) -> bool:
    normalized = normalize_text(text)
    return bool(re.search(r"\breinforcement\s+weight\b", normalized))


def is_direct_concrete_reo_setup(text: str) -> bool:
    normalized = normalize_text(text)
    return bool(re.search(r"\b(?:use\s+)?(?:concrete\s*/?\s*reo|concrete\s+reo|concrete\s*/\s*reinforcement)\b", normalized))
