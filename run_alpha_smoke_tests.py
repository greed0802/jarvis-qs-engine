from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jarvis_app.app import app
from jarvis_app.qa_runner.test_executor import TestPackExecutor


def _configure_unicode_safe_console() -> None:
    for stream in (getattr(sys, "stdout", None), getattr(sys, "stderr", None)):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="replace")
            except Exception:
                pass


def main() -> int:
    _configure_unicode_safe_console()
    parser = argparse.ArgumentParser(description="Run Jarvis v5 alpha local API smoke test packs.")
    parser.add_argument("--pack", default="alpha11_contract_negative_guards", help="Built-in pack name or path to JSON test pack.")
    parser.add_argument("--no-report", action="store_true", help="Do not write JSON/Markdown reports.")
    args = parser.parse_args()

    with TestPackExecutor(app, write_report=not args.no_report) as executor:
        result = executor.run_pack(args.pack)
    print("Jarvis v5 Alpha Test Runner")
    print(f"Pack: {result.get('pack')}")
    print("")
    for test in result.get("tests", []):
        status = "PASS" if test.get("passed") else "FAIL"
        print(f"{status} {test.get('name')}")
        if not test.get("passed"):
            for step in test.get("steps", []):
                if not step.get("passed"):
                    print(f"  FAIL step {step.get('name')} {step.get('method')} {step.get('endpoint')}")
                    for failure in step.get("failures", []):
                        print(f"    {failure.get('path')}: {failure.get('message')} actual={failure.get('actual')}")
    print("")
    print(f"Overall: {result.get('overall')}")
    print(f"Passed: {result.get('passed')}")
    print(f"Failed: {result.get('failed')}")
    if result.get("report_json"):
        print(f"Report JSON: {result.get('report_json')}")
    if result.get("report_md"):
        print(f"Report MD: {result.get('report_md')}")
    print("Safety:")
    for key, value in result.get("safety", {}).items():
        print(f"  {key}: {value}")
    return 0 if result.get("overall") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
