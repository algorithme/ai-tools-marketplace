# Authoring plugins

A **plugin** is a directory that groups one or more Claude Code components. This page explains the manifest format and the full list of supported component types. Each component type has a dedicated deep-dive linked in the matrix below.

Grumpy also supports Codex through a separate manifest and hook configuration;
see its [package maintenance notes](./plugins/grumpy-senior-engineer-workflow/codex.md#package-maintenance).

## Plugin manifest — `plugin.json`

Every plugin **should** have a `.claude-plugin/plugin.json`. The manifest is technically optional (Claude Code auto-discovers components), but it is required to set a version and metadata.

Minimal manifest:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "One-line description shown in /plugin discover."
}
```

Full manifest with all supported fields:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does.",
  "author": { "name": "Olivier Morel", "email": "olivier@devbox.ch" },
  "homepage": "https://github.com/omorel/ai-tools-marketplace",
  "repository": "https://github.com/omorel/ai-tools-marketplace",
  "license": "MIT",
  "keywords": ["example", "tutorial"],
  "skills": "./skills/",
  "commands": "./commands/",
  "agents": "./agents/",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json",
  "lspServers": "./.lsp.json",
  "outputStyles": "./output-styles/",
  "monitors": "./monitors/monitors.json",
  "userConfig": {
    "api_key": { "description": "API key for the service", "sensitive": true }
  }
}
```

Rules:
- `name` must be **kebab-case** (lowercase, hyphens, no spaces or uppercase).
- `version` must follow **semver** (`MAJOR.MINOR.PATCH`). See [adr/0002](../adr/0002-versioning-and-releases.md).
- All component paths are relative to the plugin root and must start with `./`.
- Plugin version lives in `plugin.json`, **not** in `marketplace.json`. See [adr/0002](../adr/0002-versioning-and-releases.md).

## Component matrix

| Component | Default location | Deep-dive |
|---|---|---|
| **Skills** | `skills/<name>/SKILL.md` | [docs/authoring/skills.md](./authoring/skills.md) |
| **Commands** | `commands/<name>.md` | [docs/authoring/commands.md](./authoring/commands.md) |
| **Agents** | `agents/<name>.md` | [docs/authoring/agents.md](./authoring/agents.md) |
| **Hooks** | `hooks/hooks.json` | [docs/authoring/hooks.md](./authoring/hooks.md) |
| **MCP servers** | `.mcp.json` | [docs/authoring/mcp-servers.md](./authoring/mcp-servers.md) |
| **LSP servers** | `.lsp.json` | [docs/authoring/lsp-servers.md](./authoring/lsp-servers.md) |
| **Output styles** | `output-styles/<name>.md` | [docs/authoring/output-styles.md](./authoring/output-styles.md) |
| **Monitors** | `monitors/monitors.json` | [docs/authoring/monitors.md](./authoring/monitors.md) |
| **Executables** | `bin/<name>` | [docs/authoring/executables.md](./authoring/executables.md) |
| **User config** | declared in `plugin.json` | [docs/authoring/user-config.md](./authoring/user-config.md) |
| **Channels** | declared in `plugin.json` | [docs/authoring/channels.md](./authoring/channels.md) |

> Upstream reference: [code.claude.com/docs/en/plugins-reference](https://code.claude.com/docs/en/plugins-reference)

## Plugin directory layout

```
plugins/my-plugin/
├── .claude-plugin/
│   └── plugin.json          ← manifest (name, version, description)
├── skills/
│   └── my-skill/
│       └── SKILL.md
├── commands/
│   └── quick-cmd.md
├── agents/
│   └── my-agent.md
├── hooks/
│   └── hooks.json
├── output-styles/
│   └── concise.md
├── monitors/
│   └── monitors.json
├── bin/
│   └── my-tool              ← executable, chmod +x
├── scripts/                 ← hook helper scripts
│   └── do-something.sh
├── .mcp.json
├── .lsp.json
├── CHANGELOG.md
└── README.md
```

> **Important**: `skills/`, `commands/`, `agents/`, `hooks/`, `output-styles/`, `monitors/`, and `bin/` must be at the **plugin root**, not inside `.claude-plugin/`.

## Path variables

Use these in hooks, MCP server configs, and skill content:

| Variable | Resolves to |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | Absolute path to the plugin's installation directory. Changes on update. |
| `${CLAUDE_PLUGIN_DATA}` | Persistent directory that survives plugin updates (`~/.claude/plugins/data/<id>/`). |
| `${user_config.<KEY>}` | Value of a `userConfig` key provided by the user at enable time. |

## Next step

1. Copy `templates/plugin-template` to `plugins/<your-plugin-name>/`.
2. Author your components.
3. Run `./scripts/validate.sh` to check everything.
4. Follow [docs/publishing.md](./publishing.md) to add your plugin to the catalog.
