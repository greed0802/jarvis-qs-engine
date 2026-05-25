# Bug Report

Fixed package-level Windows long path blocker:

- Error: 0x80010135 Path too long.
- Cause: generated contract_fixture_replay report filenames included long conversation/fixture slugs and were packaged under jarvis_v5/data/test_reports.
- Fix: shorter generated report names and release ZIP exclusion for generated test_reports.
