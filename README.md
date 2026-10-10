# olivier-vault

> A personal plugin marketplace for Claude Code, with Codex support in Grumpy and Humanizer.

[![Validate](https://github.com/omorel/ai-tools-marketplace/actions/workflows/validate.yml/badge.svg)](https://github.com/omorel/ai-tools-marketplace/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## Install

Claude Code:

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

For Grumpy in Codex, follow [Codex setup and compatibility](./docs/plugins/grumpy-senior-engineer-workflow/codex.md), including hook review.
For Humanizer in Codex, Claude Cowork, ChatGPT, and other assistants, see
[Humanizer setup and usage](./plugins/humanizer/README.md).

## Plugins

| Plugin | Description | Components |
|---|---|---|
| [update-manager](./plugins/update-manager/README.md) | Tiered dependency updates across ecosystems, with Renovate configuration generation. | 2 skills, hooks |
| [grumpy-senior-engineer-workflow](./plugins/grumpy-senior-engineer-workflow/README.md) | Project context, architecture decisions, planning, and approved implementation in Claude Code and Codex. | 4 shared skills, runtime hooks, 4 Claude commands |
| [humanizer](./plugins/humanizer/README.md) | Edit prose using 25 writing patterns in Claude Code and Codex, with standalone reuse in other assistants. | 1 shared skill |

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
