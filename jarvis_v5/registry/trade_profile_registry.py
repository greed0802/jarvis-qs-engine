from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path(__file__).with_name("trade_profile_registry.json")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@lru_cache(maxsize=1)
def load_trade_profile_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _word_pattern(alias: str) -> str:
    parts = [re.escape(part) for part in _norm(alias).split()]
    return r"\b" + r"\s+".join(parts) + r"\b"


def find_trade_registry_match(text: str) -> dict[str, Any] | None:
    normalized = _norm(text)
    if not normalized:
        return None
    registry = load_trade_profile_registry()
    for key, profile in (registry.get("profiles") or {}).items():
        aliases = profile.get("aliases") or [key]
        for alias in aliases:
            if re.search(_word_pattern(alias), normalized, flags=re.I):
                return {
                    "matched": True,
                    "registry_key": key,
                    "input": alias,
                    "canonical_trade": profile.get("canonical_trade"),
                    "risk": profile.get("risk"),
                    "normalization_mode": profile.get("normalization_mode"),
                    "requires_custom_quantity": bool(profile.get("requires_custom_quantity", False)),
                    "allowed_functions": profile.get("allowed_functions") or [],
                    "default_unit": profile.get("default_unit"),
                    "common_custom_quantities": profile.get("common_custom_quantities") or [],
                    "requires_clarification": profile.get("normalization_mode") == "clarify",
                    "clarification_prompt": profile.get("clarification_prompt"),
                }
    return None


def trade_registry_clarification(match: dict[str, Any]) -> dict[str, Any]:
    canonical = match.get("canonical_trade") or "this trade"
    prompt = match.get("clarification_prompt") or f"{canonical} needs measurement clarification before I update the Builder setup."
    options: list[str] = ["Cancel"]
    if match.get("registry_key") == "reinforcement":
        options = ["Use XGETCUSTOM with Reinforcement Weight unit t", "Cancel"]
    elif match.get("allowed_functions"):
        options = [f"Use {fn}" for fn in match.get("allowed_functions") or []] + ["Cancel"]
    return {
        "clarification_id": f"clar_{uuid.uuid4().hex}",
        "type": "trade_profile_requires_clarification",
        "prompt": prompt,
        "options": options,
        "expected_answer_classes": ["choice", "cancel"],
        "resolver_name": "resolve_trade_profile_registry_clarification",
        "context": {"trade_registry": match},
        "repeats": 0,
        "max_repeats": 2,
        "status": "open",
        "created_at": _now(),
        "updated_at": _now(),
    }


def clean_trade_registry_payload(match: dict[str, Any] | None) -> dict[str, Any] | None:
    if not match:
        return None
    return {
        "matched": bool(match.get("matched")),
        "registry_key": match.get("registry_key"),
        "input": match.get("input"),
        "canonical_trade": match.get("canonical_trade"),
        "risk": match.get("risk"),
        "normalization_mode": match.get("normalization_mode"),
        "requires_custom_quantity": bool(match.get("requires_custom_quantity", False)),
        "requires_clarification": bool(match.get("requires_clarification", False)),
        "allowed_functions": match.get("allowed_functions") or [],
        "default_unit": match.get("default_unit"),
        "common_custom_quantities": match.get("common_custom_quantities") or [],
    }
