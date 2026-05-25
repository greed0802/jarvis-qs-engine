from __future__ import annotations

"""Normalize natural active Builder setup wording into canonical parser grammar.

This module must not drop semantic setup tokens. It only removes conversational
wrappers so existing parsers can own slot extraction. Conflict guards are run on
both raw and canonical text by the reducer.
"""

import re
from dataclasses import dataclass
from typing import Any

from jarvis_v5.tools.builder.function_unit_compatibility import normalize_unit

NUMBER_WORDS = {"one": "1", "two": "2", "three": "3", "four": "4"}


def _replace_setup_number_words(text: str) -> str:
    out = text
    for word, number in NUMBER_WORDS.items():
        out = re.sub(rf"\bzone\s+{word}\b", f"Zone {number}", out, flags=re.I)
        out = re.sub(rf"\bhead\s+{word}\b", f"Head {number}", out, flags=re.I)
    return out


@dataclass(frozen=True)
class SetupTextNormalization:
    original_text: str
    canonical_text: str
    applied: bool = False
    reason: str | None = None
    original_unit: str | None = None
    canonical_unit: str | None = None
    unit_normalized: bool = False

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "original_text": self.original_text,
            "raw_text": self.original_text,
            "canonical_text": self.canonical_text,
            "applied": self.applied,
        }
        if self.reason:
            payload["reason"] = self.reason
        if self.original_unit:
            payload["original_unit"] = self.original_unit
        if self.canonical_unit:
            payload["canonical_unit"] = self.canonical_unit
        if self.unit_normalized:
            payload["unit_normalized"] = True
        return payload


def _normalize_clause(clause: str) -> tuple[str, str | None]:
    stripped = _replace_setup_number_words((clause or "").strip())
    if not stripped:
        return "", None

    rules: list[tuple[str, str, str]] = [
        # Unit grammar: "The unit should be m2" -> "Unit m2"
        (r"^\s*(?:the\s+)?unit\s+(?:should\s+be|is|as|to|=)\s+(no|nr|count|item|each|pcs|m2|m3|lm|m|t|kg)(?:\s*,?\s*not\s+.+?)?\s*\.?\s*$", r"Unit \1", "natural_unit"),
        (r"^\s*set\s+(?:the\s+)?unit\s+(?:as|to)\s+(no|nr|count|item|each|pcs|m2|m3|lm|m|t|kg)\s*\.?\s*$", r"Unit \1", "natural_unit"),
        (r"^\s*(?:the\s+)?unit\s+should\s+be\s+(no|nr|count|item|each|pcs|m2|m3|lm|m|t|kg)\s*\.?\s*$", r"Unit \1", "natural_unit"),
        # Combined function/unit: preserve both tokens. "Use Count, the unit should be m2" -> "Use Count Unit m2"
        (r"^\s*(use\s+.+?)[,;]?\s+(?:the\s+)?unit\s+(?:should\s+be|is|as|to|=)\s+(no|nr|count|item|each|pcs|m2|m3|lm|m|t|kg)\s*\.?\s*$", r"\1 Unit \2", "natural_function_unit"),
        # Zone grammar: "For now, Zone 1 is Old and New" -> "Zone 1: Old and New"
        (r"^\s*(?:for\s+now,?\s*)?zone\s+(\d+)\s+(?:is|are|has|have|should\s+(?:include|contain)|contains?)\s+(.+?)\s*\.?\s*$", r"Zone \1: \2", "natural_zone_values"),
        (r"^\s*make\s+zone\s+(\d+)\s+(.+?)\s*\.?\s*$", r"Zone \1: \2", "natural_zone_values"),
        # Reversed Zone grammar: "Please put Old and New under Zone 1" -> "Zone 1: Old and New"
        (r"^\s*(?:please\s+)?put\s+(.+?)\s+(?:under|in|inside|into|at|to)\s+zone\s+(\d+)\s*\.?\s*$", r"Zone \2: \1", "natural_reversed_zone_values"),
        (r"^\s*(?:for\s+)?zone\s+(\d+)\s+(?:use|set|take|has|have)\s+(.+?)\s*\.?\s*$", r"Zone \1: \2", "natural_zone_values"),
        (r"^\s*(.+?)\s+(?:are|is|should\s+be|should\s+go|go(?:es)?)\s+(?:in|inside|under|at|to)\s+zone\s+(\d+)\s*\.?\s*$", r"Zone \2: \1", "natural_reversed_zone_values"),
        (r"^\s*(.+?)\s+should\s+be\s+zone\s+(\d+)\s*\.?\s*$", r"Zone \2: \1", "natural_reversed_zone_values"),
        # Heading grammar: "Please put Zone 1 under Head 2" -> "Zone 1 at Head 2"
        (r"^\s*(?:please\s+)?put\s+zone\s+(\d+)\s+(?:under|at|to|in)\s+head\s*([1-4])\s*\.?\s*$", r"Zone \1 at Head \2", "natural_heading_assignment"),
        (r"^\s*zone\s+(\d+)\s+(?:goes\s+under|should\s+be|is|at)\s+head\s*([1-4])\s*\.?\s*$", r"Zone \1 at Head \2", "natural_heading_assignment"),
        (r"^\s*head\s*([1-4])\s+(?:should\s+be\s+)?(?:is\s+)?(?:for|to|under)\s+zone\s+(\d+)\s*\.?\s*$", r"Zone \2 at Head \1", "natural_heading_assignment"),
        (r"^\s*head\s*([1-4])\s+belongs\s+to\s+zone\s+(\d+)\s*\.?\s*$", r"Zone \2 at Head \1", "natural_heading_assignment"),
        # Level grammar: "Use levels from GF to L3" -> "Levels GF to L3"
        (r"^\s*(?:use|set)?\s*(?:the\s+)?levels?\s+(?:should\s+be|are|is|from|as)?\s*([A-Za-z0-9\s,]+?\s+to\s+[A-Za-z0-9\s]+(?:\s+with\s+.+?)?)\s*\.?\s*$", r"Levels \1", "natural_levels"),
        # Trade/function wrappers.
        (r"^\s*(?:the\s+)?trade\s+(?:should\s+be|is|as|to)\s+(.+?)\s*\.?\s*$", r"Use \1", "natural_trade"),
        (r"^\s*set\s+(?:the\s+)?function\s+(?:as|to)\s+(.+?)\s*\.?\s*$", r"Use \1", "natural_function"),
        (r"^\s*(?:the\s+)?function\s+(?:should\s+be|is)\s+(.+?)\s*\.?\s*$", r"Use \1", "natural_function"),
    ]

    for pattern, replacement, reason in rules:
        canonical = re.sub(pattern, replacement, stripped, flags=re.I).strip()
        if canonical != stripped:
            return canonical, reason
    return stripped, None


def _split_setup_clauses(text: str) -> list[str]:
    """Split setup text into clauses without losing semantic tokens."""
    protected = re.sub(r"\r\n?", "\n", text or "")
    # Keep sentence boundaries, semicolons, and newlines. Commas are not split
    # because they are often part of level/zone lists.
    raw_parts = re.split(r"(?:\n+|;|(?<=\.)\s+)", protected)
    parts: list[str] = []
    for part in raw_parts:
        cleaned = part.strip().strip(".").strip()
        if cleaned:
            parts.append(cleaned)
    return parts or [text.strip()]



_UNIT_TOKEN_RE = re.compile(
    r"\bunit\s+(no|nr|count|item|each|pcs|m2|m²|m3|m³|lm|m|t|kg|sqm|sq\.?\s*m|(?:sq|square)\s+met(?:re|er)s?)\b|\b(no|nr|count|item|each|pcs|m2|m²|m3|m³|lm|m|t|kg|sqm|sq\.?\s*m|(?:sq|square)\s+met(?:re|er)s?)\b",
    re.I,
)


def _detect_unit_evidence(text: str) -> tuple[str | None, str | None, bool]:
    for match in _UNIT_TOKEN_RE.finditer(text or ""):
        raw = match.group(1) or match.group(2)
        if not raw:
            continue
        canonical = normalize_unit(raw)
        if canonical:
            return raw, canonical, canonical != raw.strip().lower()
    return None, None, False


def normalize_active_setup_text(text: str) -> SetupTextNormalization:
    original = text or ""
    stripped = original.strip()
    if not stripped:
        return SetupTextNormalization(original_text=original, canonical_text=stripped)

    clauses = _split_setup_clauses(stripped)
    canonical_clauses: list[str] = []
    reasons: list[str] = []
    last_zone_id: str | None = None
    for clause in clauses:
        prepared_clause = _replace_setup_number_words(clause)
        zone_match = re.search(r"\bzone\s+(\d+)\b", prepared_clause, flags=re.I)
        if zone_match:
            last_zone_id = zone_match.group(1)
        elif last_zone_id and re.search(r"\bput\s+it\s+(?:under|at|to|in)\s+head\s*[1-4]\b", prepared_clause, flags=re.I):
            prepared_clause = re.sub(
                r"^\s*(?:please\s+)?put\s+it\s+(?:under|at|to|in)\s+head\s*([1-4])\s*$",
                rf"Zone {last_zone_id} at Head \1",
                prepared_clause,
                flags=re.I,
            )
        canonical, reason = _normalize_clause(prepared_clause)
        if canonical:
            canonical_clauses.append(canonical)
        if reason:
            reasons.append(reason)

    canonical_text = ". ".join(canonical_clauses).strip()
    if canonical_text and not canonical_text.endswith(".") and len(canonical_clauses) > 1:
        canonical_text += "."
    final_canonical = canonical_text or stripped
    applied = final_canonical != stripped
    original_unit, canonical_unit, unit_normalized = _detect_unit_evidence(original)
    # Prefer the final canonical unit if it differs after clause rewriting.
    _canon_original, detected_canonical_unit, detected_unit_normalized = _detect_unit_evidence(final_canonical)
    if detected_canonical_unit:
        canonical_unit = detected_canonical_unit
        unit_normalized = unit_normalized or detected_unit_normalized
    return SetupTextNormalization(
        original_text=original,
        canonical_text=final_canonical,
        applied=applied,
        reason=";".join(dict.fromkeys(reasons)) if reasons else None,
        original_unit=original_unit,
        canonical_unit=canonical_unit,
        unit_normalized=unit_normalized,
    )
