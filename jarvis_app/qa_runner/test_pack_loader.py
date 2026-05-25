from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from jarvis_v5.config import PACKAGE_ROOT
from jarvis_v5.qa_runner.test_pack_schema import TestPack

PACKS_DIR = PACKAGE_ROOT / "tests" / "packs"


class TestPackLoadError(Exception):
    """Structured error for invalid or missing imported test packs."""
    __test__ = False

    def __init__(self, error_type: str, message: str, *, details: dict[str, Any] | None = None, pack: str | None = None):
        super().__init__(message)
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.pack = pack

    def to_response(self) -> dict[str, Any]:
        return {
            "overall": "INVALID_PACK",
            "blocked": True,
            "pack": self.pack,
            "error_type": self.error_type,
            "message": self.message,
            "details": self.details,
            "safety": {
                "workbook_read_any_true": False,
                "engine_called_any_true": False,
                "excel_created_any_true": False,
                "legacy_builder_called_any_true": False,
            },
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "contract_only": True,
            "legacy_builder_called": False,
        }


def resolve_pack_path(pack: str | None) -> Path:
    name = pack or "alpha11_contract_negative_guards"
    candidate = Path(name)
    if candidate.exists():
        return candidate
    lookup_name = name if name.endswith(".json") else f"{name}.json"
    candidate = PACKS_DIR / lookup_name
    if candidate.exists():
        return candidate
    raise TestPackLoadError(
        "pack_not_found",
        f"Test pack not found: {pack}",
        details={"searched": [str(Path(name)), str(PACKS_DIR / lookup_name)]},
        pack=pack,
    )


def load_raw_test_pack(pack: str | None = None) -> tuple[Path, dict[str, Any]]:
    path = resolve_pack_path(pack)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TestPackLoadError(
            "pack_read_error",
            f"Could not read test pack: {path}",
            details={"exception": type(exc).__name__, "detail": str(exc), "path": str(path)},
            pack=pack,
        ) from exc
    try:
        data = json.loads(text)
    except JSONDecodeError as exc:
        raise TestPackLoadError(
            "json_parse_error",
            "Could not parse test pack JSON.",
            details={"line": exc.lineno, "column": exc.colno, "message": exc.msg, "path": str(path)},
            pack=pack,
        ) from exc
    if not isinstance(data, dict):
        raise TestPackLoadError(
            "bad_schema",
            "Test pack root must be a JSON object.",
            details={"path": str(path), "actual_type": type(data).__name__},
            pack=pack,
        )
    return path, data


def load_test_pack(pack: str | None = None) -> TestPack:
    path, data = load_raw_test_pack(pack)
    try:
        loaded = TestPack.model_validate(data)
    except ValidationError as exc:
        raise TestPackLoadError(
            "bad_schema",
            "Test pack schema is invalid.",
            details={"path": str(path), "errors": exc.errors()},
            pack=pack,
        ) from exc
    return loaded
