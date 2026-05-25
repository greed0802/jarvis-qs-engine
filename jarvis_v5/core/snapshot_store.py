from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any
from jarvis_v5.config import SNAPSHOTS_DIR
from jarvis_v5.core.json_store import read_json, write_json
from jarvis_v5.schemas.builder_snapshot_schema import BuilderRunSnapshot, now_iso


class SnapshotStore:
    def __init__(self, root: Path = SNAPSHOTS_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, snapshot_id: str) -> Path:
        safe = snapshot_id.replace("/", "_")
        return self.root / f"{safe}.json"

    def _active_path(self, conversation_id: str) -> Path:
        safe = conversation_id.replace("/", "_")
        return self.root / f"active_{safe}.json"

    def new_id(self) -> str:
        return f"snap_{uuid.uuid4().hex}"

    def save(self, snapshot: BuilderRunSnapshot) -> None:
        # If a different snapshot was active for this conversation, keep it but mark it superseded.
        current = self.get_active(snapshot.conversation_id)
        if current and current.snapshot_id != snapshot.snapshot_id and current.status == "current":
            current.status = "superseded"
            current.stale_reason = "newer_snapshot_created"
            current.updated_at = now_iso()
            write_json(self._path(current.snapshot_id), current.model_dump(mode="json"))

        payload = snapshot.model_dump(mode="json")
        write_json(self._path(snapshot.snapshot_id), payload)
        write_json(self._active_path(snapshot.conversation_id), {"snapshot_id": snapshot.snapshot_id})

    def get(self, snapshot_id: str | None) -> BuilderRunSnapshot | None:
        if not snapshot_id:
            return None
        data = read_json(self._path(snapshot_id))
        if not data:
            return None
        return BuilderRunSnapshot.model_validate(data)

    def get_active(self, conversation_id: str) -> BuilderRunSnapshot | None:
        pointer: dict[str, Any] | None = read_json(self._active_path(conversation_id))
        if not pointer:
            return None
        return self.get(pointer.get("snapshot_id"))

    def mark_active_stale(self, conversation_id: str, *, reason: str, active_plan_hash: str | None = None) -> BuilderRunSnapshot | None:
        snapshot = self.get_active(conversation_id)
        if not snapshot:
            return None
        if snapshot.status == "current":
            snapshot.status = "stale"
            snapshot.stale_reason = reason
            snapshot.active_plan_hash = active_plan_hash
            snapshot.updated_at = now_iso()
            write_json(self._path(snapshot.snapshot_id), snapshot.model_dump(mode="json"))
        elif active_plan_hash:
            snapshot.active_plan_hash = active_plan_hash
            snapshot.updated_at = now_iso()
            write_json(self._path(snapshot.snapshot_id), snapshot.model_dump(mode="json"))
        return snapshot
