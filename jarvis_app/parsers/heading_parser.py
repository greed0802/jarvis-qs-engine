from __future__ import annotations

import re
from typing import Any


def parse_heading_assignments(text: str) -> dict[str, Any] | None:
    """Parse lightweight Builder shell heading assignments.

    Alpha.8 stores state only. It does not generate formulas or rows.
    Supported examples:
    - Use Head 2 for Zone 1 and Head 3 for Zone 2
    - Zone 1 at Head 2, Zone 2 at Head 3
    - Start at Head 3
    """
    original = text.strip()
    if not original:
        return None

    assignments: dict[str, str] = {}

    # Use Head 2 for Zone 1 and Head 3 for Zone 2
    for head, zone in re.findall(r"\bhead\s*(\d+)\s+for\s+zone\s*(\d+)\b", original, flags=re.I):
        assignments[str(int(zone))] = f"Head{int(head)}"

    # Zone 1 at Head 2 / Zone 2 -> Head 3
    for zone, head in re.findall(r"\bzone\s*(\d+)\s*(?:at|to|->|→)\s*head\s*(\d+)\b", original, flags=re.I):
        assignments[str(int(zone))] = f"Head{int(head)}"

    # Start at Head 3. This is kept as a default start head rather than applied
    # to every zone, because alpha.8 has no full hierarchy builder yet.
    start_match = re.search(r"\bstart\s+at\s+head\s*(\d+)\b", original, flags=re.I)
    result: dict[str, Any] = {}
    if assignments:
        result["assignments"] = assignments
    if start_match:
        result["start_head"] = f"Head{int(start_match.group(1))}"
    if not result:
        return None
    result["confidence"] = 0.92
    return result
