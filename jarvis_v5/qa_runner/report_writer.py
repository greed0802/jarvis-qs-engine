from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jarvis_v5.config import TEST_REPORTS_DIR


def write_reports(result: dict[str, Any], pack_name: str) -> tuple[str, str]:
    """Write JSON/Markdown QA reports, recreating the report directory if needed.

    Alpha.12.1 could crash with FileNotFoundError when a cleaned/unzipped package
    did not contain jarvis_v5/data/test_reports. Keep this guard here instead of
    relying only on package extraction or config import side effects.
    """
    TEST_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in pack_name)
    json_path = TEST_REPORTS_DIR / f"{safe_name}_{stamp}.json"
    md_path = TEST_REPORTS_DIR / f"{safe_name}_{stamp}.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(_markdown(result), encoding="utf-8")
    return str(json_path), str(md_path)


def _markdown(result: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Jarvis QA Test Report — {result.get('pack')}")
    lines.append("")
    lines.append(f"- Version: `{result.get('version')}`")
    lines.append(f"- Overall: **{result.get('overall')}**")
    lines.append(f"- Passed: {result.get('passed')}")
    lines.append(f"- Failed: {result.get('failed')}")
    safety = result.get("safety", {})
    lines.append("")
    lines.append("## Safety aggregate")
    for key, value in safety.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Tests")
    for test in result.get("tests", []):
        status = "PASS" if test.get("passed") else "FAIL"
        lines.append(f"### {status} — {test.get('name')}")
        for step in test.get("steps", []):
            step_status = "PASS" if step.get("passed") else "FAIL"
            lines.append(f"- {step_status} `{step.get('method')} {step.get('endpoint')}` route=`{step.get('route')}`")
            for failure in step.get("failures", []):
                lines.append(f"  - `{failure.get('path')}`: {failure.get('message')}")
        lines.append("")
    failures = result.get("failures") or []
    if failures:
        lines.append("## Failures")
        for failure in failures:
            lines.append(f"- Test `{failure.get('test')}`, step `{failure.get('step')}`, path `{failure.get('path')}`: expected/assertion failed. Actual: `{failure.get('actual')}`. {failure.get('message')}")
    return "\n".join(lines) + "\n"
