from __future__ import annotations

import ast
import re
from collections import defaultdict
from pathlib import Path

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import (
    APP_VERSION,
    BUILDER_ENGINE_EXECUTION_ENABLED,
    EXCEL_OUTPUT_ENABLED,
    LEGACY_BUILDER_CALLABLE,
    WORKBOOK_READ_ENABLED,
)

ROOT = Path(__file__).resolve().parents[3]


def _release_package_files() -> list[Path]:
    ignored_parts = {"__pycache__", ".pytest_cache"}
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and not any(part in ignored_parts for part in path.parts)
    ]


def test_generated_test_report_paths_are_windows_safe_when_present() -> None:
    generated = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "jarvis_v5/data/test_reports").rglob("*")
        if path.is_file()
    ]
    long_generated = [path for path in generated if len(path) > 120]
    assert long_generated == []


def test_release_package_internal_paths_are_windows_safe() -> None:
    long_paths = [
        path.relative_to(ROOT).as_posix()
        for path in _release_package_files()
        if len(path.relative_to(ROOT).as_posix()) > 120
    ]
    assert long_paths == []


def _python_files() -> list[Path]:
    return [
        path
        for path in (ROOT / "jarvis_v5").rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def _duplicate_fastapi_routes() -> dict[tuple[str, str], list[str]]:
    route_pattern = re.compile(r"@app\.(get|post|put|delete|patch)\([\"']([^\"']+)")
    seen: dict[tuple[str, str], list[str]] = defaultdict(list)
    for path in _python_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in route_pattern.finditer(text):
            seen[(match.group(1), match.group(2))].append(path.relative_to(ROOT).as_posix())
    return {key: files for key, files in seen.items() if len(files) > 1}


def _same_file_top_level_duplicates() -> list[tuple[str, str, list[int]]]:
    duplicates: list[tuple[str, str, list[int]]] = []
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        local: dict[str, list[int]] = defaultdict(list)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                local[node.name].append(node.lineno)
        for name, lines in local.items():
            if len(lines) > 1:
                duplicates.append((path.relative_to(ROOT).as_posix(), name, lines))
    return duplicates


def _preview_policy_owner_files() -> list[str]:
    refs: list[str] = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "preview-execution-policy" in text or "evaluate_preview_execution_policy" in text:
            refs.append(path.relative_to(ROOT).as_posix())
    return sorted(refs)


def test_release_hygiene_version_and_safety_locks() -> None:
    data = TestClient(app).get("/api/version").json()
    assert data["version"] == APP_VERSION == "v5.0.0-alpha.36.3"
    assert data["execution_locks"]["builder_engine_execution_enabled"] is False
    assert data["execution_locks"]["legacy_builder_callable"] is False
    assert data["execution_locks"]["workbook_read_enabled"] is False
    assert data["execution_locks"]["excel_output_enabled"] is False
    assert BUILDER_ENGINE_EXECUTION_ENABLED is False
    assert LEGACY_BUILDER_CALLABLE is False
    assert WORKBOOK_READ_ENABLED is False
    assert EXCEL_OUTPUT_ENABLED is False


def test_no_previous_version_release_artifacts_in_root() -> None:
    root_files = {path.name for path in ROOT.iterdir() if path.is_file()}
    stale = sorted(
        name
        for name in root_files
        if (
            "alpha_27" in name
            or "alpha27" in name
            or "ALPHA_27" in name
            or "alpha_28" in name
            or "alpha28" in name
            or "ALPHA_28" in name
            or "alpha_29" in name
            or "alpha29" in name
            or "ALPHA_29" in name
        )
    )
    alpha30_stale = {
        "JARVIS_v5_0_0_alpha_30_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_30_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_30_TEST_RUN_RESULTS.txt",
        "CURRENT_BACKEND_STATUS_v5_alpha_30.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_30.md",
        "CHAT_CONTEXT_ARCHIVE_v5_alpha_30.md",
        "alpha30_all_pack_results.json",
        "START_JARVIS_V5_ALPHA_30.bat",
        "START_JARVIS_V5_ALPHA_30_SIMPLE_NO_RELOAD.bat",
        "JARVIS_v5_0_0_alpha_30_1_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_30_1_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_30_1_TEST_RUN_RESULTS.txt",
        "JARVIS_v5_0_0_alpha_30_1_WEAKNESS_TRIAGE_REPORT.md",
        "CURRENT_BACKEND_STATUS_v5_alpha_30_1.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_30_1.md",
        "CHAT_CONTEXT_ARCHIVE_v5_alpha_30_1.md",
        "alpha30_1_all_pack_results.json",
        "START_JARVIS_V5_ALPHA_30_1.bat",
        "START_JARVIS_V5_ALPHA_30_1_SIMPLE_NO_RELOAD.bat",
    }
    alpha31a_stale = {
        "JARVIS_v5_0_0_alpha_31A_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31A_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_31A_TEST_RUN_RESULTS.txt",
        "JARVIS_v5_0_0_alpha_31A_DUPLICATE_SCAN_REPORT.md",
        "JARVIS_v5_0_0_alpha_31A_PACKAGE_HYGIENE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31A_TARGETED_WEAKNESS_SUBSET_REPORT.md",
        "CURRENT_BACKEND_STATUS_v5_alpha_31A.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_31A.md",
        "CHAT_CONTEXT_ARCHIVE_v5_alpha_31A.md",
        "alpha31A_all_pack_results.json",
        "START_JARVIS_V5_ALPHA_31A.bat",
        "START_JARVIS_V5_ALPHA_31A_SIMPLE_NO_RELOAD.bat",
    }
    alpha31b_stale = {
        "JARVIS_v5_0_0_alpha_31B_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31B_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_31B_TEST_RUN_RESULTS.txt",
        "JARVIS_v5_0_0_alpha_31B_DUPLICATE_SCAN_REPORT.md",
        "JARVIS_v5_0_0_alpha_31B_PACKAGE_HYGIENE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31B_TARGETED_WEAKNESS_SUBSET_REPORT.md",
        "CURRENT_BACKEND_STATUS_v5_alpha_31B.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_31B.md",
        "CHAT_CONTEXT_ARCHIVE_v5_alpha_31B.md",
        "alpha31B_all_pack_results.json",
        "START_JARVIS_V5_ALPHA_31B.bat",
        "START_JARVIS_V5_ALPHA_31B_SIMPLE_NO_RELOAD.bat",
    }
    alpha31c_stale = {
        "JARVIS_v5_0_0_alpha_31C_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31C_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_31C_TEST_RUN_RESULTS.txt",
        "JARVIS_v5_0_0_alpha_31C_DUPLICATE_SCAN_REPORT.md",
        "JARVIS_v5_0_0_alpha_31C_PACKAGE_HYGIENE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31C_TARGETED_WEAKNESS_SUBSET_REPORT.md",
        "CURRENT_BACKEND_STATUS_v5_alpha_31C.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_31C.md",
        "CHAT_CONTEXT_ARCHIVE_v5_alpha_31C.md",
        "alpha31C_all_pack_results.json",
        "START_JARVIS_V5_ALPHA_31C.bat",
        "START_JARVIS_V5_ALPHA_31C_SIMPLE_NO_RELOAD.bat",
    }
    alpha31d_stale = {
        "JARVIS_v5_0_0_alpha_31D_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31D_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_31D_TEST_RUN_RESULTS.txt",
        "JARVIS_v5_0_0_alpha_31D_DUPLICATE_SCAN_REPORT.md",
        "JARVIS_v5_0_0_alpha_31D_PACKAGE_HYGIENE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31D_TARGETED_WEAKNESS_SUBSET_REPORT.md",
        "CURRENT_BACKEND_STATUS_v5_alpha_31D.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_31D.md",
        "CHAT_CONTEXT_ARCHIVE_v5_alpha_31D.md",
        "alpha31D_all_pack_results.json",
        "START_JARVIS_V5_ALPHA_31D.bat",
        "START_JARVIS_V5_ALPHA_31D_SIMPLE_NO_RELOAD.bat",
    }
    alpha31e_stale = {
        "JARVIS_v5_0_0_alpha_31E_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31E_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_31E_TEST_RUN_RESULTS.txt",
        "JARVIS_v5_0_0_alpha_31E_DUPLICATE_SCAN_REPORT.md",
        "JARVIS_v5_0_0_alpha_31E_PACKAGE_HYGIENE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31E_TARGETED_WEAKNESS_SUBSET_REPORT.md",
        "CURRENT_BACKEND_STATUS_v5_alpha_31E.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_31E.md",
        "CHAT_CONTEXT_ARCHIVE_v5_alpha_31E.md",
        "alpha31E_all_pack_results.json",
        "START_JARVIS_V5_ALPHA_31E.bat",
        "START_JARVIS_V5_ALPHA_31E_SIMPLE_NO_RELOAD.bat",
    }

    alpha31f1_stale = {
        "JARVIS_v5_0_0_alpha_31F_1_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31F_1_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_31F_1_TEST_RUN_RESULTS.txt",
        "JARVIS_v5_0_0_alpha_31F_1_DUPLICATE_SCAN_REPORT.md",
        "JARVIS_v5_0_0_alpha_31F_1_PACKAGE_HYGIENE_REPORT.md",
        "JARVIS_v5_0_0_alpha_31F_1_TARGETED_WEAKNESS_SUBSET_REPORT.md",
        "JARVIS_v5_0_0_alpha_31F_1_WEAKNESS_REPLAY_COMPATIBILITY_REPORT.md",
        "CURRENT_BACKEND_STATUS_v5_alpha_31F_1.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_31F_1.md",
        "CHAT_CONTEXT_ARCHIVE_v5_alpha_31F_1.md",
        "alpha31F_1_all_pack_results.json",
        "START_JARVIS_V5_ALPHA_31F_1.bat",
        "START_JARVIS_V5_ALPHA_31F_1_SIMPLE_NO_RELOAD.bat",
    }
    assert stale == []
    assert sorted(alpha30_stale & root_files) == []
    assert sorted(alpha31a_stale & root_files) == []
    assert sorted(alpha31b_stale & root_files) == []
    assert sorted(alpha31c_stale & root_files) == []
    assert sorted(alpha31d_stale & root_files) == []
    assert sorted(alpha31e_stale & root_files) == []
    assert sorted(alpha31f1_stale & root_files) == []
    assert (ROOT / "jarvis_v5/docs/version_history/alpha27").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha28").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha28_1").is_dir()


def test_current_alpha35_10_2_root_release_artifacts_exist() -> None:
    expected = {
        "JARVIS_v5_0_0_alpha_35_10_2_CHANGE_REPORT.md",
        "JARVIS_v5_0_0_alpha_35_10_2_TEST_REPORT.md",
        "JARVIS_v5_0_0_alpha_35_10_2_TEST_RUN_RESULTS.txt",
        "CURRENT_BACKEND_STATUS_v5_alpha_35_10_2.md",
        "NEXT_CHAT_HANDOFF_v5_alpha_35_10_2.md",
        "START_JARVIS_V5_ALPHA_35_10_2.bat",
        "START_JARVIS_V5_ALPHA_35_10_2_SIMPLE_NO_RELOAD.bat",
    }
    root_files = {path.name for path in ROOT.iterdir() if path.is_file()}
    assert expected.issubset(root_files)
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_6").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_7").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_7_1").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_8").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_9").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha29").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha30").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha30_1").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha31A").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha31B").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha31C").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha31D").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha31E").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha31F_1").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha32A").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha32C_1").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha33").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha33_1").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha33_2").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha34").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_1").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_2").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_3").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_3_1").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_4").is_dir()
    assert (ROOT / "jarvis_v5/docs/version_history/alpha35_5").is_dir()

def test_duplicate_route_and_same_file_definition_scans_clean() -> None:
    assert _duplicate_fastapi_routes() == {}
    assert _same_file_top_level_duplicates() == []


def test_preview_execution_policy_single_runtime_owner() -> None:
    refs = _preview_policy_owner_files()
    assert "jarvis_v5/app.py" in refs
    assert "jarvis_v5/tools/builder/preview_execution_policy.py" in refs
    assert refs.count("jarvis_v5/tools/builder/preview_execution_policy.py") == 1
    # Test and QA files may reference the endpoint, but only preview_execution_policy.py owns policy logic.
    runtime_logic_refs = [
        ref
        for ref in refs
        if not ref.startswith("jarvis_v5/tests/") and ref != "jarvis_v5/qa_runner/test_executor.py"
    ]
    assert runtime_logic_refs == ["jarvis_v5/app.py", "jarvis_v5/tools/builder/preview_execution_policy.py"]
