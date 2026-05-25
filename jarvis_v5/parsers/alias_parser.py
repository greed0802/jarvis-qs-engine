from __future__ import annotations

import re
from typing import Any


def parse_alias_edit(text: str) -> dict[str, Any] | None:
    """Parse simple alias instructions for the Builder shell plan."""
    original = text.strip()
    if not original:
        return None

    # Use Mezz as code for Mezzanine
    m = re.search(r"\buse\s+(.+?)\s+as\s+(?:code|alias)\s+for\s+(.+?)\s*$", original, flags=re.I)
    if m:
        alias = m.group(1).strip(" ,;.")
        canonical = m.group(2).strip(" ,;.")
        if alias and canonical:
            return {"action": "set", "aliases": {canonical: alias}, "confidence": 0.9}

    # Change Mezz to Mezzanine / Change Mezzanine to Mezz
    m = re.search(r"\bchange\s+(.+?)\s+to\s+(.+?)\s*$", original, flags=re.I)
    if m and ("mezz" in original.lower() or "mezzanine" in original.lower()):
        old = m.group(1).strip(" ,;.")
        new = m.group(2).strip(" ,;.")
        if old and new:
            return {"action": "replace", "old": old, "new": new, "confidence": 0.8}
    return None
