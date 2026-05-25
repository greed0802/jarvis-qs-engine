from __future__ import annotations

import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import UploadFile
from jarvis_v5.config import ATTACHMENTS_DIR
from jarvis_v5.schemas.message_schema import AttachmentMeta


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AttachmentStore:
    def __init__(self, root: Path = ATTACHMENTS_DIR):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def register_meta(self, meta: AttachmentMeta, *, bound_to_task_id: str | None = None) -> dict:
        attachment_id = meta.attachment_id or f"att_{uuid.uuid4().hex}"
        return {
            "workbook_id": attachment_id,
            "attachment_id": attachment_id,
            "filename": meta.filename,
            "content_type": meta.content_type,
            "size_bytes": meta.size_bytes,
            "saved_path": meta.saved_path,
            "source": "upload",
            "bound_to_task_id": bound_to_task_id,
            "created_at": now_iso(),
        }

    def save_upload(self, upload: UploadFile) -> dict:
        # Alpha 6.1: package cleanup or manual deletion can remove data/attachments
        # after the store was created. Recreate the folder at write time so upload
        # never fails with a raw FileNotFoundError. This still saves metadata only;
        # no workbook parsing or sheet inspection is performed.
        self.root.mkdir(parents=True, exist_ok=True)
        attachment_id = f"att_{uuid.uuid4().hex}"
        safe_name = Path(upload.filename or "upload.bin").name or "upload.bin"
        target = self.root / f"{attachment_id}_{safe_name}"
        with target.open("wb") as f:
            shutil.copyfileobj(upload.file, f)
        return {
            "workbook_id": attachment_id,
            "attachment_id": attachment_id,
            "filename": upload.filename or target.name,
            "content_type": upload.content_type,
            "size_bytes": target.stat().st_size,
            "saved_path": str(target),
            "source": "upload",
            "bound_to_task_id": None,
            "created_at": now_iso(),
        }
