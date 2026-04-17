# olivier-vault

> A personal Claude Code plugin marketplace — Skills, Agents, Hooks, MCP servers, and more.

[![Validate](https://github.com/omorel/ai-tools-marketplace/actions/workflows/validate.yml/badge.svg)](https://github.com/omorel/ai-tools-marketplace/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## Install

```
/plugin marketplace add omorel/ai-tools-marketplace
```

Then install any plugin by name:

```
/plugin install <plugin-name>@olivier-vault
```

Or via the CLI:

```bash
claude plugin marketplace add omorel/ai-tools-marketplace
claude plugin install <plugin-name>@olivier-vault
```

## Plugins

| Plugin | Description | Components |
|---|---|---|
| *(coming soon)* | — | — |

*Plugins are added in follow-up PRs. Watch the repo or check back soon.*

## Supported component types

This marketplace supports every plugin component type in the Claude Code plugin spec:

| Component | What it does |
|---|---|
| **Skills** | `/command-name` shortcuts — prompt templates invocable by name |
| **Commands** | Flat-file skills (simpler format, same invocation) |
| **Agents** | Specialised subagents with their own model, tools, and system prompt |
| **Hooks** | Event handlers for lifecycle events (PostToolUse, SessionStart, …) |
| **MCP servers** | External tool integrations via Model Context Protocol |
| **LSP servers** | Language intelligence (diagnostics, go-to-definition, hover) |
| **Output styles** | Response formatting presets |
| **Monitors** | Background watchers that stream context into the session |
| **Executables** | CLI helpers added to `PATH` during the session |
| **User config** | Plugin-specific secrets and settings prompted at install |
| **Channels** | Message sources (Telegram, Slack, …) injected into the conversation |

## Documentation

| | |
|---|---|
| [Getting started](./docs/getting-started.md) | Install and use plugins |
| [Authoring plugins](./docs/authoring.md) | `plugin.json` schema + component matrix |
| [Publishing a plugin](./docs/publishing.md) | Add your plugin to the marketplace |
| [Troubleshooting](./docs/troubleshooting.md) | Common errors |
| [Component deep-dives](./docs/authoring/) | Per-component authoring guides |
| [Architecture decisions](./adr/) | Why the repo is structured as it is |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). All plugins go through a PR with CI validation.

## Security

If you discover a security issue in a plugin or the marketplace infrastructure, see [SECURITY.md](./SECURITY.md) — do not open a public issue.

## License

[MIT](./LICENSE) © 2026 Olivier Morel
