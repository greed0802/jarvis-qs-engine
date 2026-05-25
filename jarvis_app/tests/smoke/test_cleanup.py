from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Callable, Any


def _windows_long_path(path: Path) -> str:
    """Return a Windows long-path-safe string for test cleanup only."""
    resolved = path.resolve()
    text = str(resolved)
    if os.name != "nt":
        return text
    if text.startswith("\\\\?\\"):
        return text
    if text.startswith("\\\\"):
        return "\\\\?\\UNC\\" + text.lstrip("\\")
    return "\\\\?\\" + text


def safe_rmtree(path: Path | str) -> None:
    """Remove a test directory tree without failing on already-missing files.

    This is test-only cleanup hygiene for Windows report directories. It ignores
    FileNotFoundError during recursive deletion because generated test report
    files may disappear between os.walk and unlink on Windows/long paths. It
    deliberately re-raises PermissionError and all other unexpected errors.
    """
    root = Path(path)
    if not root.exists():
        return

    target = _windows_long_path(root)

    def _onexc(func: Callable[..., Any], failed_path: str, exc: BaseException) -> None:
        if isinstance(exc, FileNotFoundError):
            return
        raise exc

    def _onerror(func: Callable[..., Any], failed_path: str, exc_info: tuple[type[BaseException], BaseException, object]) -> None:
        exc = exc_info[1]
        if isinstance(exc, FileNotFoundError):
            return
        raise exc

    try:
        shutil.rmtree(target, onexc=_onexc)
    except TypeError:
        # Python < 3.12 compatibility.
        try:
            shutil.rmtree(target, onerror=_onerror)
        except FileNotFoundError:
            return
    except FileNotFoundError:
        return
