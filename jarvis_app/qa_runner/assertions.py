from __future__ import annotations

from typing import Any

_MISSING = object()


def json_path_get(data: Any, path: str) -> Any:
    if not path or path == "$":
        return data
    if not path.startswith("$."):
        raise ValueError(f"Unsupported JSON path: {path}")
    current = data
    token = ""
    i = 2
    parts: list[Any] = []
    while i < len(path):
        ch = path[i]
        if ch == ".":
            if token:
                parts.append(token)
                token = ""
            i += 1
            continue
        if ch == "[":
            if token:
                parts.append(token)
                token = ""
            j = path.find("]", i)
            if j == -1:
                raise ValueError(f"Bad JSON path index: {path}")
            raw = path[i + 1:j]
            try:
                parts.append(int(raw))
            except ValueError:
                raise ValueError(f"Only numeric indexes supported in JSON path: {path}")
            i = j + 1
            continue
        token += ch
        i += 1
    if token:
        parts.append(token)

    for part in parts:
        if isinstance(part, int):
            if not isinstance(current, list) or part >= len(current):
                return _MISSING
            current = current[part]
        else:
            if not isinstance(current, dict) or part not in current:
                return _MISSING
            current = current[part]
    return current


def available_fields(data: Any) -> list[str]:
    if isinstance(data, dict):
        return sorted(str(key) for key in data.keys())
    if isinstance(data, list):
        return [f"[{idx}]" for idx in range(min(len(data), 20))]
    return []


def _ok(value: Any, assertion: dict[str, Any]) -> tuple[bool, str]:
    if "equals" in assertion:
        expected = assertion["equals"]
        if value is _MISSING:
            return False, "Path not found"
        return value == expected, f"expected {expected!r}, got {value!r}"
    if "not_equals" in assertion:
        expected = assertion["not_equals"]
        if value is _MISSING:
            return True, "path not found, so it does not equal value"
        return value != expected, f"did not expect {expected!r}, got {value!r}"
    if assertion.get("exists") is True:
        return value is not _MISSING, "Path not found"
    if assertion.get("not_exists") is True:
        return value is _MISSING, f"path exists with {value!r}"
    if assertion.get("is_true") is True:
        if value is _MISSING:
            return False, "Path not found"
        return value is True, f"expected true, got {value!r}"
    if assertion.get("is_false") is True:
        if value is _MISSING:
            return False, "Path not found"
        return value is False, f"expected false, got {value!r}"
    if "contains" in assertion:
        expected = assertion["contains"]
        if value is _MISSING:
            return False, "Path not found"
        return expected in value, f"expected {value!r} to contain {expected!r}"
    if "not_contains" in assertion:
        expected = assertion["not_contains"]
        if value is _MISSING:
            return True, "path not found, so it does not contain value"
        return expected not in value, f"expected {value!r} not to contain {expected!r}"
    if "includes_all" in assertion:
        expected_items = assertion["includes_all"]
        if value is _MISSING:
            return False, "Path not found"
        missing = [item for item in expected_items if item not in value]
        return not missing, f"missing items {missing!r} from {value!r}"
    return False, "unsupported assertion operator"


def evaluate_assertions(response_json: Any, assertions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    top_fields = available_fields(response_json)
    for assertion in assertions or []:
        path = assertion.get("path", "$")
        try:
            value = json_path_get(response_json, path)
            passed, message = _ok(value, assertion)
        except Exception as exc:
            value = _MISSING
            passed = False
            message = f"assertion error: {type(exc).__name__}: {exc}"
        result = {
            "path": path,
            "passed": passed,
            "message": message,
            "assertion": assertion,
            "actual": None if value is _MISSING else value,
        }
        if value is _MISSING:
            result["error_type"] = "path_not_found"
            result["available_top_level_fields"] = top_fields
            result["hint"] = (
                f"Path {path} does not exist on this endpoint response. "
                "This may be a bad assertion for this endpoint; check nested fields or remove the assertion."
            )
        results.append(result)
    return results
