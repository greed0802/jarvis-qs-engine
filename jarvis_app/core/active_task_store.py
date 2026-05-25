from __future__ import annotations

import uuid
from pathlib import Path
from jarvis_app.config import ACTIVE_TASKS_DIR
from jarvis_app.core.json_store import read_json, write_json
from jarvis_app.schemas.active_task_schema import ActiveTask, ToolName, TaskStatus


class ActiveTaskStore:
    def __init__(self, root: Path = ACTIVE_TASKS_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, task_id: str) -> Path:
        safe = task_id.replace("/", "_")
        return self.root / f"{safe}.json"

    def create(self, conversation_id: str, tool: ToolName, status: TaskStatus, plan: dict | None = None) -> ActiveTask:
        task = ActiveTask(
            task_id=f"task_{uuid.uuid4().hex}",
            conversation_id=conversation_id,
            tool=tool,
            status=status,
            plan=plan or {},
        )
        task.touch()
        self.save(task)
        return task

    def get(self, task_id: str | None) -> ActiveTask | None:
        if not task_id:
            return None
        data = read_json(self._path(task_id))
        if not data:
            return None
        return ActiveTask.model_validate(data)

    def save(self, task: ActiveTask) -> None:
        task.touch()
        write_json(self._path(task.task_id), task.model_dump(mode="json"))
