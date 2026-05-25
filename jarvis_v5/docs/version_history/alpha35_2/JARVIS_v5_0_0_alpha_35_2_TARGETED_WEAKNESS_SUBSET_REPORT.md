# Jarvis v5.0.0-alpha.35.3 Targeted Weakness Subset Report

Attack packs tested:

- 004_malicious_conversation_id_policy_review_1.json
- 005_malicious_conversation_id_policy_review_2.json

Result:

- No HTTP status 0 exceptions
- No AttributeError
- No OSError / WinError 87 / Errno 22
- No UnicodeEncodeError
- Safety aggregate remained false
- Only remaining failures are `normal_id_*` safe ID preservation expectations, classified as over-strict attack-pack expectations.
