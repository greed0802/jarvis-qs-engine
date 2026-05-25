from __future__ import annotations

import uuid
from pathlib import Path
from jarvis_v5.config import CONVERSATIONS_DIR
from jarvis_v5.core.conversation_id_safety import sanitize_conversation_id, safe_conversation_storage_stem
from jarvis_v5.core.json_store import read_json, write_json
from jarvis_v5.schemas.conversation_schema import ConversationState


def normalize_conversation_id(conversation_id: str | None) -> str | None:
    """Return a safe usable conversation id, or None for placeholders/missing ids."""
    return sanitize_conversation_id(conversation_id)


class ConversationStore:
    def __init__(self, root: Path = CONVERSATIONS_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, conversation_id: str) -> Path:
        safe = safe_conversation_storage_stem(conversation_id)
        return self.root / f"{safe}.json"

    def create(self, mode: str = "ask_first", conversation_id: str | None = None) -> ConversationState:
        normalized_id = normalize_conversation_id(conversation_id)
        state = ConversationState(
            conversation_id=normalized_id or f"chat_{uuid.uuid4().hex}",
            current_mode=mode,
        )  # type: ignore[arg-type]
        state.touch()
        self.save(state)
        return state

    def get_or_create(self, conversation_id: str | None, mode: str = "ask_first") -> ConversationState:
        normalized_id = normalize_conversation_id(conversation_id)
        if normalized_id:
            existing = self.get(normalized_id)
            if existing:
                existing.current_mode = mode  # type: ignore[assignment]
                existing.touch()
                self.save(existing)
                return existing
            return self.create(mode=mode, conversation_id=normalized_id)
        return self.create(mode=mode)

    def get(self, conversation_id: str) -> ConversationState | None:
        data = read_json(self._path(conversation_id))
        if not data:
            return None
        return ConversationState.model_validate(data)

    def save(self, state: ConversationState) -> None:
        state.touch()
        write_json(self._path(state.conversation_id), state.model_dump(mode="json"))
