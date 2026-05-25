from __future__ import annotations

import re
from typing import Any

INSTRUCTION_BOUNDARY_RE = re.compile(r"\b(?:use\s+head|levels?|preview|review|export)\b", flags=re.I)


def _strip_boundary(text: str) -> str:
    match = INSTRUCTION_BOUNDARY_RE.search(text)
    if match:
        return text[: match.start()].strip(" ,;.")
    return text.strip(" ,;.")


def clean_zone_value(raw: str) -> str:
    value = raw.strip(" \t\r\n,;/")
    value = re.sub(r"^(?:contains?|should\s+contain|should\s+be|must\s+contain)\s+", "", value, flags=re.I).strip()
    return value.strip(" ,;.")


def split_values(text: str) -> list[str]:
    cleaned = _strip_boundary(text)
    cleaned = re.sub(r"\s*(?:/|,|\band\b|&)\s*", "|", cleaned, flags=re.I)
    values: list[str] = []
    for part in cleaned.split("|"):
        value = clean_zone_value(part)
        if value and value.lower() not in {"zone", "zones"} and value not in values:
            values.append(value)
    return values



def parse_zone_set_edits(text: str) -> list[dict[str, Any]]:
    """Parse one or more zone set phrases from a single setup sentence.

    Example: "Zone 1: Old and New; Zone 2: External and Internal".
    This is state-only parsing; it does not infer formulas or rows.
    """
    original = text.strip()
    if not original:
        return []
    matches = list(re.finditer(r"\bzone\s*(\d+)\s*(?::|=|contains?|should\s+contain)\s*", original, flags=re.I))
    if not matches:
        return []
    edits: list[dict[str, Any]] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(original)
        raw_values = original[start:end].strip(" ;,.\n\t")
        values = split_values(raw_values)
        if values:
            edits.append({"action": "set", "zone_id": int(match.group(1)), "values": values, "confidence": 0.95})
    return edits

def parse_zone_edit(text: str) -> dict[str, Any] | None:
    original = text.strip()
    if not original:
        return None

    # Zone 1: Old and New / Zone 1 contains Old and New
    m = re.search(r"\bzone\s*(\d+)\s*(?::|=|contains?|should\s+contain)\s*(.+)$", original, flags=re.I | re.S)
    if m:
        zone_id = int(m.group(1))
        values = split_values(m.group(2))
        if values:
            return {"action": "set", "zone_id": zone_id, "values": values, "confidence": 0.95}

    # Add Same to Zone 1 / Add Same as new value to Zone 1
    m = re.search(r"\badd\s+(.+?)\s+(?:as\s+new\s+value\s+)?to\s+zone\s*(\d+)\b", original, flags=re.I | re.S)
    if m:
        values = split_values(m.group(1))
        if values:
            return {"action": "append", "zone_id": int(m.group(2)), "values": values, "confidence": 0.9}

    # Replace Old with Toad in Zone 1
    m = re.search(r"\breplace\s+(.+?)\s+with\s+(.+?)\s+in\s+zone\s*(\d+)\b", original, flags=re.I | re.S)
    if m:
        old = clean_zone_value(m.group(1))
        new = clean_zone_value(m.group(2))
        if old and new:
            return {"action": "replace", "zone_id": int(m.group(3)), "old_value": old, "new_value": new, "confidence": 0.9}

    # Change Old to Toad (ambiguous zone)
    m = re.search(r"\bchange\s+(.+?)\s+to\s+(.+?)\s*$", original, flags=re.I | re.S)
    if m:
        old = clean_zone_value(m.group(1))
        new = clean_zone_value(m.group(2))
        if old and new:
            return {"action": "ambiguous_replace", "old_value": old, "new_value": new, "confidence": 0.75}

    return None
