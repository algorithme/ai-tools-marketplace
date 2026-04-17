# 0002 — Versioning strategy — semver in `plugin.json`

**Status**: Accepted

## Context

Plugin versions can be set in two places:
- In the plugin's own `.claude-plugin/plugin.json` (`"version": "1.0.0"`).
- In the marketplace catalog's `marketplace.json` plugin entry (`"version": "1.0.0"`).

The Claude Code spec states that when both are set, `plugin.json` wins silently. This silent override is easy to miss and causes the marketplace entry to be ignored.

Additionally: what versioning scheme and cadence should plugins use?

## Decision

**Version lives in `plugin.json`, never in `marketplace.json` plugin entries.**

- Each plugin's `.claude-plugin/plugin.json` carries its own `version` field.
- `marketplace.json` plugin entries omit the `version` field entirely.
- The marketplace catalog itself has a `metadata.version` (e.g. `"0.1.0"`) that tracks the catalog schema version, not individual plugin versions.

**Versioning follows semantic versioning (semver):**

| Change type | Bump |
|---|---|
| Breaking change to a skill interface or hook contract | MAJOR |
| New component added to an existing plugin | MINOR |
| Bug fix, typo, documentation improvement | PATCH |

**Release flow:**

```
bump version in plugin.json
  │
  ▼
update CHANGELOG.md in plugin directory
  │
  ▼
open PR → CI validates → merge to main
  │
  ▼
users get the update on their next /plugin marketplace update
```

## Consequences

### Positive
- No ambiguity about which version is authoritative.
- `plugin.json` is the single source of truth for a plugin; reading one file is enough.
- Claude Code's update detection (version comparison) works correctly.

### Negative / trade-offs
- Contributors must remember to bump `version` in `plugin.json` before every meaningful change. If they forget, existing users will not receive the update due to caching.
- The `scripts/validate.sh` does not currently enforce version bumps on PRs — this is a known gap.

### Neutral
- The marketplace `metadata.version` is bumped manually when the catalog schema or overall structure changes in a breaking way.
