from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime, timezone
from jarvis_v5.config import ADAPTERS_DIR
from jarvis_v5.core.json_store import read_json, write_json
from jarvis_v5.schemas.builder_adapter_schema import BuilderAdapterDryRunResult


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AdapterDryRunStore:
    def __init__(self, root: Path = ADAPTERS_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, adapter_input_id: str) -> Path:
        safe = adapter_input_id.replace('/', '_')
        return self.root / f"{safe}.json"

    def _latest_path(self, conversation_id: str) -> Path:
        safe = conversation_id.replace('/', '_')
        return self.root / f"latest_{safe}.json"

    def save(self, result: BuilderAdapterDryRunResult | dict[str, Any]) -> None:
        payload = result.model_dump(mode='json') if hasattr(result, 'model_dump') else result
        adapter_input_id = payload.get('adapter_input_id')
        conversation_id = payload.get('conversation_id')
        if not adapter_input_id or not conversation_id:
            return
        write_json(self._path(adapter_input_id), payload)
        write_json(self._latest_path(conversation_id), {'adapter_input_id': adapter_input_id})

    def get(self, adapter_input_id: str | None) -> BuilderAdapterDryRunResult | None:
        if not adapter_input_id:
            return None
        data = read_json(self._path(adapter_input_id))
        if not data:
            return None
        return BuilderAdapterDryRunResult.model_validate(data)

    def get_latest(self, conversation_id: str) -> BuilderAdapterDryRunResult | None:
        pointer = read_json(self._latest_path(conversation_id))
        if not pointer:
            return None
        return self.get(pointer.get('adapter_input_id'))


    def mark_snapshot_stale(self, snapshot_id: str | None, *, reason: str = "source_snapshot_is_stale") -> list[BuilderAdapterDryRunResult]:
        """Mark any adapter dry-run records that were created from a stale snapshot.

        This does not delete or rewrite adapter_input. It only marks/display freshness
        so /api/plan, Review, and router trace do not make an old dry run look current.
        """
        if not snapshot_id:
            return []
        updated: list[BuilderAdapterDryRunResult] = []
        for path in self.root.glob("adapter_*.json"):
            data = read_json(path)
            if not data or data.get("snapshot_id") != snapshot_id:
                continue
            if data.get("freshness") == "stale" and data.get("adapter_status") == "stale_due_to_snapshot":
                try:
                    updated.append(BuilderAdapterDryRunResult.model_validate(data))
                except Exception:
                    pass
                continue
            data["freshness"] = "stale"
            data["stale_reason"] = reason
            data["snapshot_status"] = "stale"
            data["adapter_status"] = "stale_due_to_snapshot"
            data["updated_at"] = now_iso()
            validation = data.get("validation") or {}
            validation["valid_for_dry_run"] = False
            validation["valid_for_future_engine"] = False
            issues = validation.get("issues") or []
            if reason not in issues:
                issues.append(reason)
            validation["issues"] = issues
            data["validation"] = validation
            write_json(path, data)
            try:
                updated.append(BuilderAdapterDryRunResult.model_validate(data))
            except Exception:
                pass
        return updated
