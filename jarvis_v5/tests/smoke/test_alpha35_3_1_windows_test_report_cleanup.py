from __future__ import annotations

from pathlib import Path

from jarvis_v5.tests.smoke.test_cleanup import safe_rmtree


def test_alpha35_6_safe_rmtree_removes_nested_report_tree(tmp_path: Path) -> None:
    report_dir = tmp_path / "test_reports" / "contract_fixture_replay"
    report_dir.mkdir(parents=True)
    long_name = "replay_20260519_014224_4c32011c_alpha19_pack_wall_clean_wall_types_xgetwallarea_zone1_head2_gf_l.json"
    report_file = report_dir / long_name
    report_file.write_text('{"ok": true}', encoding="utf-8")

    safe_rmtree(tmp_path / "test_reports")

    assert not (tmp_path / "test_reports").exists()


def test_alpha35_6_safe_rmtree_ignores_missing_tree(tmp_path: Path) -> None:
    missing = tmp_path / "test_reports"

    safe_rmtree(missing)

    assert not missing.exists()
