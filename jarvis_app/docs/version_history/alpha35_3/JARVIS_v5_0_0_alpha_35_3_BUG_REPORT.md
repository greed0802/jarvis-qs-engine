# v5.0.0-alpha.35.3 BUG_REPORT

Fixed no-active workbook-read policy questions falling to general_stub and no-active workbook content-read commands sometimes falling to general_stub/new_builder_task_shell. Remaining 009-011 failures are from intentionally inconsistent expected routes in the attack packs, while runtime safety and deterministic non-fallback routing are correct.
