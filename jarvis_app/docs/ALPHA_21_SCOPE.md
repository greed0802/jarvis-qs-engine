# v5.0.0-alpha.21 — Function/Unit Compatibility Guard + Fixture Report Filename Hygiene, no engine

Scope:
- Block or clarify incompatible CostX function/unit pairs, especially XGETCOUNT + m2.
- Preserve valid XGETCOUNT count units such as no and nr.
- Preserve XGETWALLAREA + m2 and XGETCUSTOM custom quantity flows.
- Shorten contract fixture replay report filenames to avoid Windows path-length failures.
- Keep all no-engine safety locks closed.

Not in scope:
- Builder engine call.
- Legacy Builder import/call.
- Workbook reading/parsing.
- Formula generation.
- Excel output.
- Formatter, QA Checker, O&A, UI redesign, or current Jarvis replacement.
