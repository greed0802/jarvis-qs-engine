# JARVIS v5.0.0-alpha.35.3 Bug Report

Fixed hygiene bugs:
1. TestPackExecutor lacked deterministic close/context-manager support, which likely caused Windows dev endpoint file-access issues around pack attachment execution.
2. /api/dev/run-smoke-tests created TestPackExecutor without closing it.
3. run_alpha_smoke_tests.py printed raw Unicode failure details, causing UnicodeEncodeError on Windows cp1252 consoles for attack packs containing emoji.

Not fixed in this build:
- malicious conversation_id/path sanitization
- policy chat routing gaps
- active content-read safe-block route gaps
- workbook-read preflight wording ambiguity
