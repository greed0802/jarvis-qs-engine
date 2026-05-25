# Weakness Replay Compatibility Cleanup — alpha.31F.1

Alpha.31E full 8,000-test replay improved from 5,985 / 8,000 to 7,470 / 8,000.

Remaining failures after alpha.31E:

- 300 historical alpha.30 version-lock artifacts
- 30 active action diagnostic alias gaps
- 200 minimal-pair route ownership failures

Alpha.31F.1 fixes only the diagnostic alias gap by adding `active_task_action_language.matched=true` metadata for exact active actions.

Minimal pair route ownership is deferred to alpha.32A.
