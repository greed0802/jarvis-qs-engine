# JARVIS v5.0.0-alpha.35.3 Targeted Weakness Subset Report

Attack packs 004 and 005 were rerun after Unicode-safe output patch.
Result: both complete without UnicodeEncodeError.
Logical failures remain expected because malicious conversation_id sanitization is intentionally out of scope for alpha.35.3.
Safety aggregate remains false for workbook read, engine call, Excel creation, and legacy Builder call.
