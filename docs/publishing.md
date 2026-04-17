# Publishing a plugin

This guide walks you through adding a new plugin to the `olivier-vault` marketplace.

## Flow

```
copy template ──▶ author components ──▶ validate ──▶ add to catalog ──▶ open PR
```

## 1. Copy the plugin template

```bash
cp -r templates/plugin-template plugins/<your-plugin-name>
```

Plugin directory names must be **kebab-case** (e.g. `git-workflow`, not `GitWorkflow` or `git_workflow`).

## 2. Author your components

Edit the files inside `plugins/<your-plugin-name>/`. Refer to the [component matrix](./authoring.md#component-matrix) and the deep-dive guide for each component you use.

At minimum, update:
- `.claude-plugin/plugin.json` — set `name`, `version`, `description`.
- `CHANGELOG.md` — add the initial `## [1.0.0]` entry.
- `README.md` — describe what the plugin does and how to use it.

## 3. Run validation

```bash
./scripts/validate.sh
```

Fix any errors before continuing. See [docs/troubleshooting.md](./troubleshooting.md) for common issues.

## 4. Add the plugin to the catalog

Open `.claude-plugin/marketplace.json` and append an entry to the `plugins` array:

```json
{
  "name": "your-plugin-name",
  "source": "your-plugin-name",
  "description": "One sentence describing what the plugin does.",
  "author": { "name": "Your Name" },
  "license": "MIT"
}
```

The `source` field resolves via `metadata.pluginRoot: "./plugins"` — you do not need to write `"./plugins/your-plugin-name"`.

**Do not** set `version` here. Version lives in `plugin.json`. See [adr/0002](../adr/0002-versioning-and-releases.md).

## 5. Open a pull request

Push your branch and open a PR against `main`. The PR template checklist will remind you of the required steps.

## Version bumps

When you modify an existing plugin:

1. Bump the version in `plugins/<name>/.claude-plugin/plugin.json`.
2. Add a changelog entry in `plugins/<name>/CHANGELOG.md`.
3. Run `./scripts/validate.sh`.
4. Open a PR.

If you forget to bump the version, existing users will not receive the update (Claude Code skips re-installs of unchanged versions).

## Relative-path source limitation

Plugins with `source: "<name>"` (relative path via `pluginRoot`) only work when users add the marketplace via git:

```
/plugin marketplace add omorel/ai-tools-marketplace    ✓  works
/plugin marketplace add https://example.com/marketplace.json  ✗  relative paths fail
```

This is by design. See [adr/0001](../adr/0001-monorepo-with-relative-paths.md) for the trade-off discussion.

## Plugin graduation

When a plugin outgrows the monorepo (CI requirements, external collaborators, large assets), graduate it to its own repository. See the graduation policy in [adr/0001](../adr/0001-monorepo-with-relative-paths.md#plugin-graduation-policy).
