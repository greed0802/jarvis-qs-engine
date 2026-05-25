from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from jarvis_v5.config import (
    APP_VERSION,
    PACKAGE_ROOT,
    ACTIVE_TASKS_DIR,
    ADAPTERS_DIR,
    ATTACHMENTS_DIR,
    CONTRACTS_DIR,
    PREFLIGHTS_DIR,
    EXECUTIONS_DIR,
    CONVERSATIONS_DIR,
    EVENTS_DIR,
    SNAPSHOTS_DIR,
    LEGACY_IMPORT_AUDITS_DIR,
)
from jarvis_v5.qa_runner.assertions import evaluate_assertions, json_path_get
from jarvis_v5.qa_runner.report_writer import write_reports
from jarvis_v5.qa_runner.test_pack_loader import TestPackLoadError, load_test_pack
from jarvis_v5.qa_runner.test_pack_schema import TestPack, TestStep


_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")
FIXTURES_DIR = PACKAGE_ROOT / "tests" / "fixtures"

KNOWN_ROUTES = {
    "new_builder_task_shell",
    "active_task_slot_edit",
    "active_task_slot_edit_needs_clarification",
    "active_task_edit_unhandled",
    "clarification_resolved",
    "attachment_bind",
    "builder_snapshot_created",
    "builder_snapshot_blocked",
    "builder_adapter_dry_run",
    "builder_adapter_dry_run_blocked",
    "builder_engine_contract_created",
    "builder_engine_contract_blocked",
    "builder_engine_contract_replay",
    "builder_engine_contract_latest_replay",
    "builder_engine_boundary_audit",
    "builder_engine_boundary_audit_blocked",
    "active_task_preview_stub",
    "active_task_review",
    "builder_engine_preflight_ready",
    "builder_engine_preflight_blocked",
    "builder_engine_execution_blocked",
    "builder_legacy_bridge_shadow_probe",
    "builder_preview_execution_policy",
    "builder_safe_workbook_path_resolver_dry_run",
    "builder_workbook_read_preflight_dry_run",
    "builder_contract_fixture_replay",
    "builder_contract_fixture_replay_blocked",
    "builder_legacy_import_boundary_audit",
    "builder_legacy_import_boundary_audit_latest",
    "builder_legacy_import_boundary_audit_latest_not_found",
    "active_task_export_stub",
    "active_task_new_command_confirmation",
    "formatter_handoff_needs_confirmation",
    "choose_tool",
    "no_active_prompt_injection_safe_block",
    "no_active_action_needs_active_task",
    "general_stub",
    "general_chat",
    "active_task_general_help",
    "active_task_non_mutating_language",
    "feedback_read_only",
    "attachment_received_no_active_task",
    "attachment_save_failed",
    "clarification_gate",
    "clarification_blocked_action",
    "clarification_cancelled",
    "active_task_cancelled",
    "active_task_start_new",
    "active_task_action_stub",
    "builder_engine_contract_replay_not_found",
    "builder_engine_contract_latest_not_found",
    "debug_create_test_clarification",
    "dev_smoke_tests_completed",
    "registry_requirement_check",
    "registry_advisory_metadata_only",
    "registry_tools",
    "registry_capabilities",
    "registry_connectors",
    "registry_models",
    "active_task_context_unhandled",
    "registry_voice_assistants",
    "registry_ecosystem_adapters",
    "registry_rfi_templates",
    "registry_file_requirements",
    "registry_scope_advisors",
    "registry_source_authorities",
    "registry_execution_policies",
    "builder_workbook_metadata_probe_approval",
    "builder_workbook_sheet_name_probe_approval",
    "builder_workbook_read_policy_review",
}


ALLOWED_ENDPOINT_PATTERNS = [
    re.compile(r"^/api/version$"),
    re.compile(r"^/api/chat$"),
    re.compile(r"^/api/attach$"),
    re.compile(r"^/api/plan/[^/]+$"),
    re.compile(r"^/api/builder/create-snapshot$"),
    re.compile(r"^/api/builder/adapter-dry-run$"),
    re.compile(r"^/api/builder/engine-contract$"),
    re.compile(r"^/api/builder/engine-contract/[^/]+$"),
    re.compile(r"^/api/builder/engine-contract/latest/[^/]+$"),
    re.compile(r"^/api/builder/engine-boundary-audit$"),
    re.compile(r"^/api/builder/engine-preflight$"),
    re.compile(r"^/api/builder/engine-execution-request$"),
    re.compile(r"^/api/builder/contract-fixture-replay$"),
    re.compile(r"^/api/builder/legacy-import-boundary-audit$"),
    re.compile(r"^/api/builder/legacy-bridge-shadow-probe$"),
    re.compile(r"^/api/builder/preview-execution-policy$"),
    re.compile(r"^/api/builder/safe-workbook-path-resolver-dry-run$"),
    re.compile(r"^/api/builder/workbook-read-preflight-dry-run$"),
    re.compile(r"^/api/builder/workbook-metadata-probe-approval$"),
    re.compile(r"^/api/builder/workbook-sheet-name-probe-approval$"),
    re.compile(r"^/api/builder/workbook-read-policy-review$"),
    re.compile(r"^/api/builder/legacy-import-boundary-audit/latest/[^/]+$"),
    re.compile(r"^/api/debug/create-test-clarification$"),
    re.compile(r"^/api/dev/run-smoke-tests$"),
    re.compile(r"^/api/dev/validate-test-pack$"),
    re.compile(r"^/api/registry/tools$"),
    re.compile(r"^/api/registry/capabilities$"),
    re.compile(r"^/api/registry/connectors$"),
    re.compile(r"^/api/registry/models$"),
    re.compile(r"^/api/registry/execution-policies$"),
    re.compile(r"^/api/registry/source-authorities$"),
    re.compile(r"^/api/registry/scope-advisors$"),
    re.compile(r"^/api/registry/file-requirements$"),
    re.compile(r"^/api/registry/rfi-templates$"),
    re.compile(r"^/api/registry/ecosystem-adapters$"),
    re.compile(r"^/api/registry/voice-assistants$"),
    re.compile(r"^/api/registry/requirement-check$"),
]


def _blank_safety() -> dict[str, bool]:
    return {
        "workbook_read_any_true": False,
        "engine_called_any_true": False,
        "excel_created_any_true": False,
        "legacy_builder_called_any_true": False,
    }


def invalid_pack_result(error: TestPackLoadError, *, write_report: bool = False) -> dict[str, Any]:
    result = error.to_response()
    result.update({
        "version": APP_VERSION,
        "passed": 0,
        "failed": 0,
        "tests": [],
        "failures": [],
        "report_json": None,
        "report_md": None,
    })
    if write_report:
        # Only write reports for parseable packs. Invalid external packs often have
        # unusable names/paths, so return the structured error directly.
        pass
    return result


class TestPackExecutor:
    __test__ = False

    def __init__(self, app, write_report: bool = True):
        self.client = TestClient(app)
        self.write_report = write_report
        self.context: dict[str, Any] = {}

    def close(self) -> None:
        close = getattr(self.client, "close", None)
        if callable(close):
            close()

    def __enter__(self) -> "TestPackExecutor":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False

    def run_pack(self, pack: str | None = None) -> dict[str, Any]:
        self._clear_runtime_test_state()
        try:
            loaded = load_test_pack(pack)
        except TestPackLoadError as exc:
            return invalid_pack_result(exc, write_report=self.write_report)

        self.context = {}
        preflight = validate_loaded_pack(loaded)
        tests = []
        failures = []
        safety_seen = _blank_safety()
        for case in loaded.tests:
            test_result = self._run_case(case, safety_seen)
            tests.append(test_result)
            if not test_result["passed"]:
                for step in test_result["steps"]:
                    for failure in step.get("failures", []):
                        failures.append({"test": case.name, "step": step.get("name"), **failure})
        result = {
            "overall": "PASS" if not failures else "FAIL",
            "version": APP_VERSION,
            "pack": loaded.pack_name,
            "passed": sum(1 for item in tests if item["passed"]),
            "failed": sum(1 for item in tests if not item["passed"]),
            "safety": safety_seen,
            "preflight": preflight,
            "compatibility_warnings": preflight.get("warnings", []),
            "tests": tests,
            "failures": failures,
        }
        if self.write_report:
            try:
                json_path, md_path = write_reports(result, loaded.pack_name)
                result["report_json"] = json_path
                result["report_md"] = md_path
            except Exception as exc:
                result["overall"] = "FAIL"
                result["error_type"] = "report_write_error"
                result["message"] = f"Could not write QA test report: {type(exc).__name__}: {exc}"
                result["report_json"] = None
                result["report_md"] = None
                result["failures"].append({
                    "test": "__report_writer__",
                    "step": "write_reports",
                    "path": "$",
                    "error_type": "report_write_error",
                    "message": result["message"],
                    "actual": None,
                })
        return result

    def _clear_runtime_test_state(self) -> None:
        """Start each pack from a clean local alpha state."""
        for root in [
            CONVERSATIONS_DIR,
            ACTIVE_TASKS_DIR,
            EVENTS_DIR,
            SNAPSHOTS_DIR,
            ADAPTERS_DIR,
            CONTRACTS_DIR,
            PREFLIGHTS_DIR,
            EXECUTIONS_DIR,
            ATTACHMENTS_DIR,
            LEGACY_IMPORT_AUDITS_DIR,
        ]:
            root.mkdir(parents=True, exist_ok=True)
            for item in root.iterdir():
                if item.name == ".keep":
                    continue
                if item.is_file():
                    item.unlink()

    def _run_case(self, case, safety_seen: dict[str, bool]) -> dict[str, Any]:
        steps = []
        passed = True
        for step in case.steps:
            step_result = self._run_step(step)
            self._update_safety(step_result.get("response_json"), safety_seen)
            steps.append(step_result)
            if not step_result["passed"]:
                passed = False
        return {"name": case.name, "passed": passed, "steps": steps}

    def _resolve_value(self, value: Any) -> Any:
        if isinstance(value, str):
            def repl(match):
                key = match.group(1)
                found = self.context.get(key)
                return "" if found is None else str(found)
            return _VAR_PATTERN.sub(repl, value)
        if isinstance(value, list):
            return [self._resolve_value(item) for item in value]
        if isinstance(value, dict):
            return {key: self._resolve_value(item) for key, item in value.items()}
        return value

    def _run_step(self, step: TestStep) -> dict[str, Any]:
        endpoint = self._resolve_value(step.endpoint)
        method = step.method.upper()
        response = None
        status_code = None
        compatibility_warnings = validate_step_compatibility(step)
        try:
            if not _endpoint_allowed(endpoint):
                raise ValueError(f"Endpoint not allowed by alpha QA runner: {endpoint}")
            if method == "GET":
                response = self.client.get(endpoint)
            elif method == "POST":
                files = list(step.files or [])
                data = self._resolve_value(step.form or step.data or {})
                if step.file_fixture:
                    fixture_path = FIXTURES_DIR / step.file_fixture
                    if not fixture_path.exists():
                        raise FileNotFoundError(f"Fixture not found: {fixture_path}")
                    files.append(type("FixtureSpec", (), {
                        "field": "file",
                        "path": str(fixture_path),
                        "filename": fixture_path.name,
                        "content_type": _guess_content_type(fixture_path),
                    })())
                if files:
                    file_payload = {}
                    open_files = []
                    try:
                        for spec in files:
                            path = self._resolve_path(self._resolve_value(spec.path))
                            fh = open(path, "rb")
                            open_files.append(fh)
                            file_payload[spec.field] = (spec.filename or path.name, fh, spec.content_type)
                        response = self.client.post(endpoint, data=data, files=file_payload)
                    finally:
                        for fh in open_files:
                            fh.close()
                else:
                    response = self.client.post(endpoint, json=self._resolve_value(step.json_body or {}))
            else:
                raise ValueError(f"Unsupported method: {method}")
            status_code = response.status_code
            try:
                payload = response.json()
            except Exception:
                payload = {"raw_text": response.text}
        except Exception as exc:
            payload = {
                "exception": type(exc).__name__,
                "detail": str(exc),
                "error_type": _step_error_type(exc),
                "workbook_read": False,
                "engine_called": False,
                "excel_created": False,
                "legacy_builder_called": False,
            }
            status_code = 0

        failures = []
        if status_code not in (200,):
            failures.append({"path": "$", "message": f"HTTP status {status_code}", "actual": payload})
        assertion_results = evaluate_assertions(payload, self._resolve_value(step.assertions or []))
        for item in assertion_results:
            if not item["passed"]:
                failures.append(item)
        if not failures and step.save:
            for name, path in step.save.items():
                try:
                    value = json_path_get(payload, path)
                    self.context[name] = value
                except Exception:
                    pass
        return {
            "name": step.name,
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "passed": not failures,
            "route": payload.get("route") if isinstance(payload, dict) else None,
            "reason": payload.get("reason") if isinstance(payload, dict) else None,
            "compatibility_warnings": compatibility_warnings,
            "failures": failures,
            "assertions": assertion_results,
            "response_json": payload,
        }

    def _resolve_path(self, path_value: str) -> Path:
        path = Path(path_value)
        if path.exists():
            return path
        candidate = PACKAGE_ROOT.parent / path_value
        if candidate.exists():
            return candidate
        candidate = PACKAGE_ROOT / path_value
        if candidate.exists():
            return candidate
        raise FileNotFoundError(path_value)

    def _update_safety(self, payload: Any, safety_seen: dict[str, bool]) -> None:
        if not isinstance(payload, dict):
            return
        text = json.dumps(payload)
        if '"workbook_read": true' in text:
            safety_seen["workbook_read_any_true"] = True
        if '"engine_called": true' in text:
            safety_seen["engine_called_any_true"] = True
        if '"excel_created": true' in text:
            safety_seen["excel_created_any_true"] = True
        if '"legacy_builder_called": true' in text:
            safety_seen["legacy_builder_called_any_true"] = True


def _endpoint_allowed(endpoint: str) -> bool:
    return any(pattern.match(endpoint) for pattern in ALLOWED_ENDPOINT_PATTERNS)


def _guess_content_type(path: Path) -> str:
    if path.suffix.lower() in {".xlsx", ".xlsm"}:
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return "application/octet-stream"


def _step_error_type(exc: Exception) -> str:
    if isinstance(exc, FileNotFoundError):
        return "fixture_not_found"
    if isinstance(exc, ValueError):
        return "step_not_allowed"
    return "step_execution_error"


def validate_loaded_pack(pack: TestPack) -> dict[str, Any]:
    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for case in pack.tests:
        saw_builder_start = False
        saw_attach = False
        saw_trade = False
        saw_function = False
        saw_unit = False
        saw_zone = False
        saw_head = False
        saw_levels = False
        saw_snapshot = False
        saw_adapter = False
        for step in case.steps:
            warnings.extend(validate_step_compatibility(step, case.name))
            text = ""
            if step.json_body and isinstance(step.json_body.get("text"), str):
                text = step.json_body.get("text", "").lower()
            endpoint = step.endpoint
            if "build" in text and "boq" in text:
                saw_builder_start = True
            if endpoint == "/api/attach" and (step.file_fixture or step.files):
                saw_attach = True
            if any(token in text for token in ["wall types", "doors", "windows", "structural", "concrete"]):
                saw_trade = True
            if any(token in text for token in ["xget", "count", "steel surface", "formworks"]):
                saw_function = True
            if any(token in text for token in ["unit", " m2", " no", " m3", " t"]):
                saw_unit = True
            if "zone" in text:
                saw_zone = True
            if "head" in text:
                saw_head = True
            if "level" in text or "levels" in text or "gf" in text:
                saw_levels = True
            if endpoint == "/api/builder/create-snapshot":
                saw_snapshot = True
            if endpoint == "/api/builder/adapter-dry-run":
                saw_adapter = True
            for assertion in step.assertions or []:
                if assertion.get("path") == "$.route" and "equals" in assertion:
                    expected = assertion["equals"]
                    if expected not in KNOWN_ROUTES:
                        warnings.append({
                            "type": "unknown_expected_route",
                            "test": case.name,
                            "step": step.name,
                            "expected": expected,
                            "known_routes": sorted(KNOWN_ROUTES),
                        })
                if assertion.get("path") in {"$.workbook_read", "$.engine_called", "$.excel_created", "$.legacy_builder_called", "$.contract_only"}:
                    # These top-level fields exist on adapter/contract/replay responses but not every endpoint.
                    # Warn only when a test asserts them on endpoints where the alpha API is not expected to
                    # expose those fields at top level.
                    endpoint_allows_top_safety = (
                        endpoint in {"/api/builder/create-snapshot", "/api/builder/adapter-dry-run", "/api/builder/engine-contract", "/api/builder/engine-boundary-audit", "/api/builder/engine-preflight", "/api/builder/engine-execution-request", "/api/builder/contract-fixture-replay", "/api/builder/legacy-import-boundary-audit", "/api/builder/legacy-bridge-shadow-probe", "/api/builder/preview-execution-policy", "/api/builder/safe-workbook-path-resolver-dry-run", "/api/builder/workbook-read-preflight-dry-run", "/api/builder/workbook-metadata-probe-approval", "/api/builder/workbook-sheet-name-probe-approval"}
                        or endpoint.startswith("/api/builder/engine-contract/")
                    )
                    if not endpoint_allows_top_safety:
                        warnings.append({
                            "type": "possibly_endpoint_specific_safety_path",
                            "test": case.name,
                            "step": step.name,
                            "path": assertion.get("path"),
                            "message": "Top-level safety fields are not returned by every endpoint; prefer endpoint-specific nested fields or assert only on adapter/contract/preview responses.",
                        })
            if endpoint == "/api/attach" and step.json_body and step.json_body.get("file"):
                warnings.append({
                    "type": "attach_json_file_not_supported",
                    "test": case.name,
                    "step": step.name,
                    "message": "Use file_fixture instead of json.file for /api/attach.",
                })
            if endpoint == "/api/builder/engine-contract":
                expects_created = any(a.get("path") == "$.route" and a.get("equals") == "builder_engine_contract_created" for a in (step.assertions or []))
                if expects_created and not all([saw_builder_start, saw_attach, saw_trade, saw_function, saw_unit, saw_zone, saw_head, saw_levels, saw_snapshot, saw_adapter]):
                    warnings.append({
                        "type": "contract_creation_expected_but_setup_steps_missing",
                        "test": case.name,
                        "step": step.name,
                        "message": "This test expects contract creation but does not include the full required Builder setup, snapshot, and adapter dry run before it.",
                        "missing_setup_seen_flags": {
                            "builder_start": saw_builder_start,
                            "attach": saw_attach,
                            "trade": saw_trade,
                            "function": saw_function,
                            "unit": saw_unit,
                            "zone": saw_zone,
                            "head": saw_head,
                            "levels": saw_levels,
                            "snapshot": saw_snapshot,
                            "adapter": saw_adapter,
                        },
                    })
    return {
        "overall": "WARN" if warnings and not errors else ("INVALID" if errors else "PASS"),
        "valid_schema": not errors,
        "can_run": not errors,
        "warnings": warnings,
        "errors": errors,
    }


def validate_step_compatibility(step: TestStep, test_name: str | None = None) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    if step.endpoint == "/api/attach" and step.json_body and step.json_body.get("file"):
        warnings.append({
            "type": "attach_json_file_not_supported",
            "test": test_name,
            "step": step.name,
            "message": "Use file_fixture instead of json.file for /api/attach.",
        })
    if step.endpoint == "/api/attach" and not (step.file_fixture or step.files):
        warnings.append({
            "type": "attach_missing_file_fixture",
            "test": test_name,
            "step": step.name,
            "message": "Attach steps should use file_fixture: Test.xlsx or a files entry.",
        })
    return warnings
