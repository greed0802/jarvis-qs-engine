from io.excel_reader import load_boq
from core.normalize import normalize_boq
from engine.excel_diff_engine import compare_boq
from output.excel_report import export_diff

def test_excel_diff():
    old = load_boq("old.xlsx")
    new = load_boq("new.xlsx")

    old = normalize_boq(old)
    new = normalize_boq(new)

    diff = compare_boq(old, new)

    export_diff(diff, "jarvis-tests/excel_diff/reports/diff_output.xlsx")

    assert diff is not None