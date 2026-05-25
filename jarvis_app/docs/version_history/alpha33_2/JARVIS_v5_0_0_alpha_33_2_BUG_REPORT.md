# Jarvis v5.0.0-alpha.33.2 Bug Report

Bug: stale release-artifact smoke test expected alpha.33 root files after alpha.33.1 packaging.

Local evidence: pytest reported 1 failed, 274 passed.

Root cause: `test_current_alpha33_root_release_artifacts_exist` used hardcoded alpha33 artifact names while the current package root contained alpha33_1 names.

Fix: update the package hygiene test to current alpha33_2 artifact names for this release.

Runtime impact: none.
