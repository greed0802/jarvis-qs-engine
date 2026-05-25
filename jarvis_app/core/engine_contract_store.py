from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from jarvis_v5.config import CONTRACTS_DIR
from jarvis_v5.core.json_store import read_json, write_json
from jarvis_v5.schemas.builder_engine_contract_schema import BuilderEngineContract


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EngineContractStore:
    def __init__(self, root: Path = CONTRACTS_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, contract_id: str) -> Path:
        return self.root / f"{contract_id.replace('/', '_')}.json"

    def _latest_path(self, conversation_id: str) -> Path:
        return self.root / f"latest_{conversation_id.replace('/', '_')}.json"

    def _latest_blocked_path(self, conversation_id: str) -> Path:
        return self.root / f"latest_blocked_{conversation_id.replace('/', '_')}.json"

    def save(self, contract: BuilderEngineContract | dict[str, Any]) -> None:
        payload = contract.model_dump(mode="json") if hasattr(contract, "model_dump") else contract
        contract_id = payload.get("contract_id")
        conversation_id = payload.get("conversation_id")
        if not contract_id or not conversation_id:
            return
        write_json(self._path(contract_id), payload)
        write_json(self._latest_path(conversation_id), {"contract_id": contract_id})

    def save_blocked_attempt(self, conversation_id: str, payload: dict[str, Any]) -> None:
        if not conversation_id:
            return
        attempt = {
            "conversation_id": conversation_id,
            "created_at": now_iso(),
            "route": payload.get("route"),
            "reason": payload.get("reason"),
            "message": payload.get("message"),
            "snapshot_id": payload.get("snapshot_id"),
            "adapter_input_id": payload.get("adapter_input_id"),
            "contract_id": payload.get("contract_id"),
            "missing_required": payload.get("missing_required") or [],
            "validation": payload.get("validation") or {},
            "workbook_read": bool(payload.get("workbook_read", False)),
            "engine_called": bool(payload.get("engine_called", False)),
            "excel_created": bool(payload.get("excel_created", False)),
            "contract_created": bool(payload.get("contract_created", False)),
        }
        write_json(self._latest_blocked_path(conversation_id), attempt)

    def get_latest_blocked_attempt(self, conversation_id: str) -> dict[str, Any] | None:
        return read_json(self._latest_blocked_path(conversation_id))

    def get(self, contract_id: str | None) -> BuilderEngineContract | None:
        if not contract_id:
            return None
        data = read_json(self._path(contract_id))
        if not data:
            return None
        return BuilderEngineContract.model_validate(data)

    def get_latest(self, conversation_id: str) -> BuilderEngineContract | None:
        pointer = read_json(self._latest_path(conversation_id))
        if not pointer:
            return None
        return self.get(pointer.get("contract_id"))
