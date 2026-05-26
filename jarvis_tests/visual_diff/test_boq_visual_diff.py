from core.boq_diff_engine import compare_boq
from renderers.html_renderer import render_html

def test_visual_diff():
    old = [
        {"id": "A1", "qty": 10},
        {"id": "A2", "qty": 5}
    ]

    new = [
        {"id": "A1", "qty": 12},
        {"id": "A3", "qty": 8}
    ]

    diff = compare_boq(old, new)
    html = render_html(diff)

    assert "Missing Items" in html