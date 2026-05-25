# JARVIS v5.0.0-alpha.34 Bug Report

No existing runtime bug was fixed.

The build adds a new controlled boundary for a previously unavailable capability: explicit sheet-name probe approval.

Observed development issue: the existing `Test.xlsx` fixture was text-only and not a valid workbook. A new test fixture `SheetProbe.xlsx` was added for alpha.34 sheet-name tests.
