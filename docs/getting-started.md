# Getting started

**olivier-vault** is a personal Claude Code plugin marketplace. This guide shows you how to add it to your Claude Code installation and install plugins from it.

## Prerequisites

- Claude Code installed and running.
- The `initialization` branch (or `main` once published) accessible at `omorel/ai-tools-marketplace`.

## Add the marketplace

```
/plugin marketplace add omorel/ai-tools-marketplace
```

This clones the repo and registers it locally as `olivier-vault`.

**Or via CLI:**

```bash
claude plugin marketplace add omorel/ai-tools-marketplace
```

## Browse available plugins

```
/plugin discover
```

Filter by marketplace:

```
/plugin discover @olivier-vault
```

## Install a plugin

```
/plugin install <plugin-name>@olivier-vault
```

Example:

```
/plugin install my-skill@olivier-vault
```

Choose a scope:

| Scope | When to use |
|---|---|
| `user` (default) | Plugin available in every project |
| `project` | Plugin shared with your team via `.claude/settings.json` |
| `local` | Plugin for this project only, not committed |

```
/plugin install my-skill@olivier-vault --scope project
```

## Update plugins

```
/plugin marketplace update olivier-vault
```

This pulls the latest `marketplace.json` and updates installed plugins to their newest versions.

## Remove a plugin

```
/plugin uninstall my-skill@olivier-vault
```

## Remove the marketplace

```
/plugin marketplace remove olivier-vault
```

> Removing the marketplace also uninstalls all plugins from it. To only refresh, use `update` instead.

## Auto-install for a project

To have team members automatically prompted to install this marketplace when they open your project, add the following to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "olivier-vault": {
      "source": {
        "source": "github",
        "repo": "omorel/ai-tools-marketplace"
      }
    }
  }
}
```

## Troubleshooting

See [docs/troubleshooting.md](./troubleshooting.md) for common install and validation errors.
