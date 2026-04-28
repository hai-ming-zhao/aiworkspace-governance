# Changelog

## 0.1.0

- Introduce a read-only Git declaration scanner for AI-assisted local workspaces.
- Classify changed paths as `ALLOW`, `REVIEW`, or `BLOCK` before staging.
- Add boundary-aware path matching, sensitive filename tiers, hidden excluded paths, unknown project review flags, and `--fail-on-block`.
- Include default rules, documentation, templates, tests, and a sanitized example workspace.
