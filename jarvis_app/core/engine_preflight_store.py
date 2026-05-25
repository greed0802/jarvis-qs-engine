from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime, timezone

from jarvis_v5.config import PREFLIGHTS_DIR
from jarvis_v5.core.json_store import read_json, write_json


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EnginePreflightStore:
    """Local JSON store for alpha.16 no-engine preflight reports.

    Stores validation-only preflight payloads. It never calls the Builder engine,
    reads workbook contents, or creates Excel output.
    """

    def __init__(self, root: Path = PREFLIGHTS_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, preflight_id: str) -> Path:
        return self.root / f"{preflight_id.replace('/', '_')}.json"

    def _latest_path(self, conversation_id: str) -> Path:
        return self.root / f"latest_{conversation_id.replace('/', '_')}.json"

    def save(self, payload: dict[str, Any]) -> None:
        preflight_id = payload.get("preflight_id")
        conversation_id = payload.get("conversation_id")
        if not preflight_id or not conversation_id:
            return
        write_json(self._path(preflight_id), payload)
        write_json(self._latest_path(conversation_id), {"preflight_id": preflight_id})

    def get(self, preflight_id: str | None) -> dict[str, Any] | None:
        if not preflight_id:
            return None
        return read_json(self._path(preflight_id))

    def get_latest(self, conversation_id: str) -> dict[str, Any] | None:
        pointer = read_json(self._latest_path(conversation_id))
        if not pointer:
            return None
        return self.get(pointer.get("preflight_id"))
