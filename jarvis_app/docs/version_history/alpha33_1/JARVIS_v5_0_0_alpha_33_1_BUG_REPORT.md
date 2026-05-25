# Jarvis v5.0.0-alpha.33.1 Bug Report

## Bug fixed
Windows local pytest failed four smoke tests because owner-scan tests expected POSIX paths such as `jarvis_v5/app.py`, while Windows returned `jarvis_v5\app.py`.

## Root cause
Affected tests used `str(path.relative_to(root))`, which is OS-dependent.

## Fix
Use `path.relative_to(root).as_posix()` in affected smoke-test owner scans.

## Runtime impact
None.
