# Plugin templates

This directory contains copy-paste starters for new plugins.

## How to use

```bash
cp -r templates/plugin-template plugins/<your-plugin-name>
```

Then:

1. Rename the plugin: update `name` in `.claude-plugin/plugin.json`.
2. Set the initial `version` (`1.0.0` for a new plugin).
3. Update `description` in `plugin.json` and the skill's `SKILL.md`.
4. Author your components (see `docs/authoring.md`).
5. Run `./scripts/validate.sh`.
6. Add an entry to `.claude-plugin/marketplace.json`.
7. Open a PR following `docs/publishing.md`.

## Available templates

| Template | Contents |
|---|---|
| `plugin-template/` | Minimal plugin with one skill — starting point for any plugin |

More templates (hook-only, mcp-server, agent-focused) will be added as the marketplace grows.
