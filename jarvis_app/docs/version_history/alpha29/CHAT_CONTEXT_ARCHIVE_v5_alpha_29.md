# Chat Context Archive — v5.0.0-alpha.29

This archive captures the user-visible decisions for alpha.29.

Confirmed context:

- alpha.28.1 was accepted as clean package hygiene baseline.
- Cross-file helper duplicates are documented only.
- alpha.29 scope is a metadata-only safe workbook path resolver dry run.
- Internal contracts can contain `saved_path`, but public responses must not return raw path values or forbidden exact raw path keys.
- Dormant code must be documented as reserved/watchlist instead of deleted due to lost context.

Decision:

- Add a dedicated resolver owner and endpoint.
- Keep workbook open/read disabled.
- Add dormant-code preservation documentation.
- Add package cleanup/version tag hygiene rule.
