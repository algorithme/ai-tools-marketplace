# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project purpose

A personal Claude Code plugin marketplace (`olivier-vault`) that catalogs Skills, Agents, Hooks, MCP servers, LSP servers, output-styles, monitors, executables, user-config, and channels — every component type from the Claude Code plugin spec.

## Repository layout

```
ai-tools-marketplace/
├── .claude-plugin/marketplace.json   ← catalog (name: "olivier-vault")
├── .github/workflows/validate.yml   ← CI (calls scripts/validate.sh)
├── adr/                             ← Architecture Decision Records
├── docs/                            ← user and contributor documentation
│   ├── getting-started.md
│   ├── authoring.md                 ← component matrix + plugin.json schema
│   ├── publishing.md
│   ├── troubleshooting.md
│   └── authoring/                   ← one file per component type
├── plugins/                         ← all plugins (relative-path sources)
│   └── <plugin-name>/
│       ├── .claude-plugin/plugin.json
│       ├── skills/ / commands/ / agents/ / hooks/ / …
│       └── README.md
├── schemas/                         ← JSON Schema for marketplace and plugin manifests
├── scripts/validate.sh              ← validation authority
└── templates/plugin-template/      ← starter for new plugins
```

## Validation

Always run before opening a PR:

```bash
./scripts/validate.sh
```

The script runs: `jq` → `ajv` (JSON Schema) → `yq` (YAML frontmatter) → `shellcheck` → kebab-case lint → `claude plugin validate` (best-effort).

See [adr/0003](./adr/0003-validation-and-ci.md) for rationale.

## Adding a plugin

1. `cp -r templates/plugin-template plugins/<kebab-case-name>`
2. Author components; set `name` and `version` in `plugin.json`.
3. Run `./scripts/validate.sh`.
4. Append entry to `.claude-plugin/marketplace.json` (no `version` field in entry — lives in `plugin.json`).
5. Open a PR. Use PR template checklist.

See [docs/publishing.md](./docs/publishing.md) for the full workflow.

## Key conventions

- **Plugin names**: kebab-case only (`my-plugin`, not `MyPlugin` or `my_plugin`).
- **Version**: lives in `plugin.json`, never in `marketplace.json` plugin entries (spec: manifest wins silently if both are set).
- **Files per PR**: soft cap of 1 000 lines of diff.
- **ADRs**: write one for every significant architectural decision. Template in `adr/README.md`.
- **Docs**: prefer many small files (`<150 lines`) over a single large file (see [adr/0004](./adr/0004-documentation-structure.md)).

## Architecture decisions

See `adr/` for the full list. Quick summary:

| # | Decision |
|---|---|
| 0001 | Monorepo with relative-path sources; `pluginRoot: "./plugins"` |
| 0002 | Semver in `plugin.json`; version not set in marketplace entries |
| 0003 | `scripts/validate.sh` is the validation authority; `claude plugin validate` is best-effort |
| 0004 | Modular docs — one file per topic |

## Local testing

```bash
# Add marketplace locally
claude plugin marketplace add ./

# Install a plugin
claude plugin install <name>@olivier-vault

# Update
claude plugin marketplace update olivier-vault
```

## Build / lint / test commands

There is no build step. The only "test" command is:

```bash
./scripts/validate.sh
```

When the project evolves (e.g. compiled MCP server binaries), update this file.
