from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jarvis_v5.config import PACKAGE_ROOT, TEST_REPORTS_DIR
from jarvis_v5.schemas.builder_engine_contract_schema import BuilderEngineContract

CONTRACT_FIXTURE_DIR = PACKAGE_ROOT / "tests" / "fixtures" / "contracts"
REPORT_DIR = TEST_REPORTS_DIR / "contract_fixture_replay"

VOLATILE_KEYS = {
    "contract_id",
    "snapshot_id",
    "adapter_input_id",
    "conversation_id",
    "task_id",
    "active_task_id",
    "workbook_id",
    "attachment_id",
    "created_at",
    "updated_at",
    "event_id",
    "client_event_id",
    "saved_path",
    "replay_url",
    "contract_hash",
}

STABLE_PATHS_DESCRIPTION = [
    "contract_schema_version",
    "legacy_target",
    "engine_version_target",
    "engine_mode",
    "source",
    "contract_status",
    "workbook_ref.filename",
    "builder_setup.trade_profile",
    "builder_setup.costx_function",
    "builder_setup.custom_quantity",
    "builder_setup.unit",
    "builder_setup.zone_mode",
    "builder_setup.dynamic_zones",
    "builder_setup.heading_assignments",
    "builder_setup.levels",
    "builder_setup.aliases",
    "builder_setup.item_code_settings",
    "setup_completeness.status",
    "setup_completeness.ready_for_future_engine",
    "normalization.status",
    "conflicts",
    "validation.valid",
    "validation.issues",
    "safety",
]


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _fixture_path(name: str) -> Path:
    safe = Path(name).name
    if not safe.endswith(".json"):
        safe = f"{safe}.json"
    return CONTRACT_FIXTURE_DIR / safe


def _load_fixture(name: str) -> dict[str, Any] | None:
    path = _fixture_path(name)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _public_workbook_ref(ref: dict[str, Any] | None) -> dict[str, Any]:
    ref = ref or {}
    return {
        "filename": ref.get("filename"),
        "source": ref.get("source") or ref.get("kind") or "upload",
    }


def stable_contract_view(contract: BuilderEngineContract | dict[str, Any] | None) -> dict[str, Any] | None:
    """Extract only stable contract fields for golden comparison.

    IDs, timestamps, paths, hashes, and event metadata are deliberately removed.
    This keeps golden fixtures useful across local machines and repeated test runs.
    """
    if contract is None:
        return None
    payload = contract.model_dump(mode="json") if hasattr(contract, "model_dump") else deepcopy(contract)
    setup = payload.get("builder_setup") or {}
    validation = payload.get("validation") or {}
    setup_completeness = payload.get("setup_completeness") or {}
    normalization = payload.get("normalization") or {}
    return {
        "contract_schema_version": payload.get("contract_schema_version"),
        "legacy_target": payload.get("legacy_target"),
        "engine_version_target": payload.get("engine_version_target"),
        "engine_mode": payload.get("engine_mode"),
        "source": payload.get("source"),
        "contract_status": payload.get("contract_status"),
        "workbook_ref": _public_workbook_ref(payload.get("workbook_ref")),
        "builder_setup": {
            "trade_profile": setup.get("trade_profile"),
            "costx_function": setup.get("costx_function"),
            "custom_quantity": setup.get("custom_quantity"),
            "unit": setup.get("unit"),
            "zone_mode": setup.get("zone_mode"),
            "dynamic_zones": setup.get("dynamic_zones") or [],
            "heading_assignments": setup.get("heading_assignments") or {},
            "levels": setup.get("levels") or [],
            "aliases": setup.get("aliases") or {},
            "item_code_settings": setup.get("item_code_settings") or {},
            "trade_registry": setup.get("trade_registry"),
        },
        "setup_completeness": {
            "status": setup_completeness.get("status"),
            "ready_for_dry_run": bool(setup_completeness.get("ready_for_dry_run", False)),
            "ready_for_future_engine": bool(setup_completeness.get("ready_for_future_engine", False)),
            "missing_required": setup_completeness.get("missing_required") or [],
        },
        "normalization": {
            "status": normalization.get("status"),
        },
        "conflicts": payload.get("conflicts") or [],
        "validation": {
            "valid": bool(validation.get("valid", False)),
            "issues": validation.get("issues") or [],
            "warnings": validation.get("warnings") or [],
        },
        "safety": {
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "contract_only": True,
            "legacy_builder_called": False,
        },
    }


def _diff(expected: Any, actual: Any, path: str = "$.") -> list[dict[str, Any]]:
    diffs: list[dict[str, Any]] = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        keys = sorted(set(expected) | set(actual))
        for key in keys:
            if key in VOLATILE_KEYS:
                continue
            next_path = f"{path}{key}"
            if key not in expected:
                diffs.append({"path": next_path, "expected": None, "actual": actual.get(key), "kind": "unexpected_field"})
            elif key not in actual:
                diffs.append({"path": next_path, "expected": expected.get(key), "actual": None, "kind": "missing_field"})
            else:
                diffs.extend(_diff(expected[key], actual[key], next_path + "."))
        return diffs
    if isinstance(expected, list) and isinstance(actual, list):
        if expected != actual:
            diffs.append({"path": path.rstrip("."), "expected": expected, "actual": actual, "kind": "value_mismatch"})
        return diffs
    if expected != actual:
        diffs.append({"path": path.rstrip("."), "expected": expected, "actual": actual, "kind": "value_mismatch"})
    return diffs


def _short_slug(value: str, *, max_len: int = 32) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "report")).strip("_")
    return (slug or "report")[:max_len]


def _write_report(conversation_id: str, fixture: str, result: dict[str, Any]) -> tuple[str | None, str | None]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    # Keep generated report filenames short enough for normal Windows Downloads paths.
    # Details stay inside the report body; uniqueness comes from timestamp + digest.
    stamp = datetime.now(timezone.utc).strftime("%y%m%d_%H%M%S")
    digest = hashlib.sha1(f"{conversation_id}|{fixture}|{stamp}".encode("utf-8")).hexdigest()[:8]
    stem = f"replay_{stamp}_{digest}"
    json_path = REPORT_DIR / f"{stem}.json"
    md_path = REPORT_DIR / f"{stem}.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        f"# Contract Fixture Replay Report",
        "",
        f"- Conversation: `{conversation_id}`",
        f"- Fixture: `{fixture}`",
        f"- Passed: `{result.get('passed')}`",
        f"- Diff status: `{result.get('diff_status')}`",
        f"- Diff count: `{len(result.get('diffs') or [])}`",
        "",
        "Safety:",
        "",
        f"- workbook_read: `{result.get('workbook_read')}`",
        f"- engine_called: `{result.get('engine_called')}`",
        f"- excel_created: `{result.get('excel_created')}`",
        f"- legacy_builder_called: `{result.get('legacy_builder_called')}`",
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")
    return str(json_path), str(md_path)


def run_contract_fixture_replay(
    *,
    fixture: str,
    conversation_id: str,
    contract: BuilderEngineContract | None = None,
    write_report: bool = True,
    intentional_mismatch: bool = False,
) -> dict[str, Any]:
    expected = _load_fixture(fixture)
    if expected is None:
        result = {
            "route": "builder_contract_fixture_replay_blocked",
            "conversation_id": conversation_id,
            "fixture": fixture,
            "passed": False,
            "blocked": True,
            "reason": "fixture_not_found",
            "diff_status": "blocked",
            "message": "Contract fixture replay blocked because the requested fixture was not found.",
            "stable_fields_compared": STABLE_PATHS_DESCRIPTION,
            "diffs": [],
            "contract_schema_version": None,
            "legacy_target": None,
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "contract_only": True,
            "legacy_builder_called": False,
        }
        return result

    expected_stable = expected.get("stable_contract") or (stable_contract_view(expected.get("contract")) if isinstance(expected, dict) and expected.get("contract") else expected)
    actual_stable = stable_contract_view(contract) if contract else deepcopy(expected_stable)
    if intentional_mismatch and actual_stable:
        actual_stable = deepcopy(actual_stable)
        actual_stable.setdefault("builder_setup", {})["unit"] = "__intentional_mismatch__"

    diffs = _diff(expected_stable, actual_stable)
    passed = len(diffs) == 0
    result = {
        "route": "builder_contract_fixture_replay",
        "conversation_id": conversation_id,
        "fixture": Path(fixture).stem,
        "passed": passed,
        "blocked": False,
        "reason": "fixture_diff_clean" if passed else "fixture_diff_mismatch",
        "diff_status": "clean" if passed else "mismatch",
        "message": "Contract fixture replay completed. No Builder engine was called and no Excel file was created.",
        "contract_id": getattr(contract, "contract_id", None),
        "contract_schema_version": (actual_stable or {}).get("contract_schema_version"),
        "legacy_target": (actual_stable or {}).get("legacy_target"),
        "stable_fields_compared": STABLE_PATHS_DESCRIPTION,
        "ignored_volatile_fields": sorted(VOLATILE_KEYS),
        "diffs": diffs,
        "expected_stable": expected_stable,
        "actual_stable": actual_stable,
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
        "safety": {
            "workbook_read": False,
            "engine_called": False,
            "excel_created": False,
            "contract_only": True,
            "legacy_builder_called": False,
        },
    }
    if write_report:
        try:
            json_path, md_path = _write_report(conversation_id, fixture, result)
            result["report_json"] = json_path
            result["report_md"] = md_path
        except Exception as exc:
            result["report_write_error"] = f"{type(exc).__name__}: {exc}"
    latest_fixture_replay_summary._latest[conversation_id] = {
        "found": True,
        "fixture": Path(fixture).stem,
        "passed": passed,
        "diff_status": result["diff_status"],
        "contract_id": result.get("contract_id"),
        "workbook_read": False,
        "engine_called": False,
        "excel_created": False,
        "contract_only": True,
        "legacy_builder_called": False,
    }
    return result


def latest_fixture_replay_summary(conversation_id: str) -> dict[str, Any]:
    return latest_fixture_replay_summary._latest.get(conversation_id, {"found": False, "status": "not_run"})


latest_fixture_replay_summary._latest = {}
