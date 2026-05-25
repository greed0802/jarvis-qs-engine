from __future__ import annotations

import hashlib
import re

PLACEHOLDER_CONVERSATION_IDS = {"", "string", "null", "none", "undefined"}
_WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,80}$")
_UNSAFE_CHARS_RE = re.compile(r'[<>:"|?*\\/;\s]')
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def _clean_raw(conversation_id: str | None) -> str | None:
    if conversation_id is None:
        return None
    cleaned = str(conversation_id).strip()
    if cleaned.lower() in PLACEHOLDER_CONVERSATION_IDS:
        return None
    return cleaned


def _is_windows_reserved(candidate: str) -> bool:
    """Return True for Windows reserved device names or reserved-leading ids.

    Windows treats names such as CON, NUL, COM1, and LPT1 as device names,
    including when followed by extensions. For Jarvis state IDs, also reject
    ids whose first underscore/dash/dot-delimited token is reserved so values
    like CON_test or nul_case are not echoed as accepted public IDs.
    """
    upper = candidate.upper()
    first_dot = upper.split(".", 1)[0]
    first_token = re.split(r"[._-]", upper, maxsplit=1)[0]
    return first_dot in _WINDOWS_RESERVED_NAMES or first_token in _WINDOWS_RESERVED_NAMES


def is_safe_conversation_id(conversation_id: str | None) -> bool:
    """Return True only for public/storage-safe conversation ids."""
    cleaned = _clean_raw(conversation_id)
    if cleaned is None:
        return False
    if ".." in cleaned:
        return False
    if _UNSAFE_CHARS_RE.search(cleaned):
        return False
    if _CONTROL_CHARS_RE.search(cleaned):
        return False
    if _is_windows_reserved(cleaned):
        return False
    return bool(_SAFE_ID_RE.fullmatch(cleaned))


def _mapped_conversation_id(raw: str) -> str:
    digest = hashlib.sha256(raw.encode("utf-8", errors="surrogatepass")).hexdigest()[:16]
    return f"cid_{digest}"


def sanitize_conversation_id(conversation_id: str | None) -> str | None:
    """Return a safe accepted conversation id, or None for missing/placeholders.

    Safe ids are preserved exactly for backward compatibility. Unsafe ids are
    deterministically mapped to a filesystem-safe cid_<hash> token so they are
    never used directly as filenames or echoed back as accepted ids.
    """
    cleaned = _clean_raw(conversation_id)
    if cleaned is None:
        return None
    if is_safe_conversation_id(cleaned):
        return cleaned
    return _mapped_conversation_id(cleaned)


def conversation_id_was_sanitized(raw: str | None, safe: str | None) -> bool:
    cleaned = _clean_raw(raw)
    if cleaned is None:
        return False
    return safe != cleaned


def safe_conversation_storage_stem(conversation_id: str) -> str:
    """Return a safe filename stem for conversation/event state storage."""
    safe = sanitize_conversation_id(conversation_id)
    if not safe:
        # Defensive fallback; callers should normally generate chat_* before
        # storing state, but never return an unsafe or empty filename stem.
        return _mapped_conversation_id(str(conversation_id))
    return safe
