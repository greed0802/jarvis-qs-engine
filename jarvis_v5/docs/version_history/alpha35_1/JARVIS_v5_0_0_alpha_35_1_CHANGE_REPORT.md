# JARVIS v5.0.0-alpha.35.3 Change Report

Version: v5.0.0-alpha.35.3
Base: v5.0.0-alpha.35 candidate
Scope: Conversation ID / State Path Sanitization, no runtime behavior change, no workbook read.

Files changed in behavior/test scope:
- jarvis_v5/qa_runner/test_executor.py
- jarvis_v5/tests/smoke/test_alpha12_qa_runner.py
- jarvis_v5/app.py
- run_alpha_smoke_tests.py

Changes:
- Added deterministic close/context-manager support to TestPackExecutor.
- Updated alpha12 direct runner test to use context-managed executor.
- Updated /api/dev/run-smoke-tests to close TestPackExecutor after run_pack.
- Made run_alpha_smoke_tests.py Unicode-safe on Windows consoles.
- Updated version/report metadata for alpha.35.3.

No router/parser/workbook/Builder/Formatter/QA Checker/O&A/UI/Output Center/registry execution behavior changed.
