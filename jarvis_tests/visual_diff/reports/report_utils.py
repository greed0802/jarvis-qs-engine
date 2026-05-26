def save_report(html, path="jarvis-tests/visual_diff/reports/diff_report.html"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
        