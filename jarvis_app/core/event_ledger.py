from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from jarvis_v5.config import EVENTS_DIR
from jarvis_v5.core.conversation_id_safety import safe_conversation_storage_stem
from jarvis_v5.core.json_store import read_json, write_json


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventLedger:
    def __init__(self, root: Path = EVENTS_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, conversation_id: str) -> Path:
        safe = safe_conversation_storage_stem(conversation_id)
        return self.root / f"{safe}.json"

    def list_events(self, conversation_id: str) -> list[dict[str, Any]]:
        events = read_json(self._path(conversation_id), default=[])
        if not isinstance(events, list):
            return []
        return events

    def find_by_client_event_id(self, conversation_id: str, client_event_id: str | None) -> dict[str, Any] | None:
        if not client_event_id:
            return None
        for event in self.list_events(conversation_id):
            if event.get("client_event_id") == client_event_id:
                return event
        return None

    def append(self, conversation_id: str, *, client_event_id: str | None, intent: str, route: str, request: dict, response: dict) -> dict[str, Any]:
        events = self.list_events(conversation_id)
        event = {
            "event_id": f"evt_{uuid.uuid4().hex}",
            "client_event_id": client_event_id,
            "conversation_id": conversation_id,
            "intent": intent,
            "route": route,
            "request": request,
            "response": response,
            "created_at": now_iso(),
        }
        events.append(event)
        write_json(self._path(conversation_id), events)
        return event


    def router_trace(self, conversation_id: str) -> list[dict[str, Any]]:
        trace: list[dict[str, Any]] = []
        for event in self.list_events(conversation_id):
            req = event.get("request") or {}
            resp = event.get("response") or {}
            attachments = req.get("attachments") or []
            trace.append({
                "event_id": event.get("event_id"),
                "client_event_id": event.get("client_event_id"),
                "conversation_id": event.get("conversation_id"),
                "text": req.get("text") or req.get("prompt") or "",
                "has_attachment": bool(attachments),
                "intent": event.get("intent") or resp.get("intent"),
                "route": event.get("route") or resp.get("route"),
                "router_step": resp.get("router_step"),
                "reason": resp.get("reason"),
                "blocked": bool(resp.get("blocked", False)),
                "duplicate": bool(resp.get("duplicate", False)),
                "active_task_id": resp.get("active_task_id"),
                "active_task_status": resp.get("active_task_status"),
                "pending_clarification_id": resp.get("pending_clarification_id"),
                "reducer": resp.get("reducer_result"),
                "snapshot": resp.get("snapshot"),
                "adapter": resp.get("adapter"),
                "created_at": event.get("created_at"),
            })
        return trace
