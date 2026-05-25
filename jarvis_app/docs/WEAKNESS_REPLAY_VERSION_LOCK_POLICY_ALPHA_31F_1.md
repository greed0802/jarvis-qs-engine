# Weakness Replay Version Lock Policy — alpha.31F.1

The original 8,000 weakness pack is an alpha.30 reference pack. Exact version assertions against `v5.0.0-alpha.30` are historical reference locks, not current runtime defects.

Current-version replay reports must separate:

- real behavior failures
- response-shape/diagnostic gaps
- historical version-lock artifacts

Jarvis must not lie about `APP_VERSION` to satisfy old reference locks. Current builds should report the current version and document old-pack version-lock failures separately.
