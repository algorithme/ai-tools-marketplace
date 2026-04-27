# 0001 — Monorepo layout with relative-path plugin sources

**Status**: Accepted

## Context

The marketplace needs to reference plugin source code somewhere. Options considered:

1. **Monorepo**: all plugins live under `plugins/<name>/` in this same repo. `marketplace.json` uses explicit relative paths (`source: "./plugins/<name>"`).
2. **Federated repos**: each plugin lives in its own GitHub repo. `marketplace.json` uses `source: {source: "github", repo: "omorel/<name>"}`.
3. **Hybrid**: start monorepo, graduate individual plugins to their own repos when they grow large enough.

## Decision

Use the **monorepo with relative paths** layout for all initial plugins.

Plugin entries use explicit `./`-prefixed paths, as required by the Claude Code validator:

```json
{ "name": "my-plugin", "source": "./plugins/my-plugin" }
```

Note: the spec documents a `pluginRoot` shorthand that allows bare names like `"source": "my-plugin"`, but the `claude plugin validate` tool rejects that form. Always use the explicit `./plugins/<name>` form.

## Consequences

### Positive
- One PR updates plugin code and the catalog atomically — no cross-repo coordination.
- Simpler local testing: `claude plugin marketplace add ./` works out of the box.
- Relative-path sources resolve during a git clone of this repo, which is the standard install path.
- No need to manage separate repository permissions.

### Negative / trade-offs
- Relative-path plugins only work when the marketplace is added via git (not via a direct URL to `marketplace.json`). Documented in `docs/publishing.md`.
- All plugins share the same git history; a noisy plugin can crowd the log.
- If a plugin grows to need independent versioning and CI, it must be graduated to its own repo (see "Plugin graduation" below).

### Neutral
- The `schemas/marketplace.schema.json` enforces that relative-path `source` strings start with `./`, matching what `claude plugin validate` actually accepts.

## Plugin graduation policy

A plugin should be graduated to its own repository when **two or more** of the following are true:

- It has its own CI requirements (e.g. requires a specific language runtime to build).
- It has external collaborators who should not have write access to the rest of this repo.
- Its changelog grows faster than the rest of the marketplace combined.
- It bundles compiled binaries or large assets that bloat the monorepo history.

To graduate: create `omorel/<plugin-name>` on GitHub, push the plugin directory, update `marketplace.json` to use a `github` source, and open a PR removing the directory from `plugins/`.
