# MCP servers

Plugins can bundle [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) servers to give Claude access to external tools, databases, and APIs.

Upstream reference: [code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)

## File location

```
plugins/my-plugin/
└── .mcp.json
```

Or inline in `plugin.json` via the `mcpServers` field.

## .mcp.json format

```json
{
  "mcpServers": {
    "my-db": {
      "command": "${CLAUDE_PLUGIN_ROOT}/bin/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_URL": "${user_config.db_url}"
      }
    }
  }
}
```

| Field | Required | Notes |
|---|---|---|
| `command` | Yes | Binary to execute. Use `${CLAUDE_PLUGIN_ROOT}` for bundled binaries. |
| `args` | No | Array of arguments. |
| `env` | No | Environment variables. Supports `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, and `${user_config.*}`. |
| `cwd` | No | Working directory for the server process. |

## Using npm-based servers

If the server is distributed via npm, use `npx`:

```json
{
  "mcpServers": {
    "my-api": {
      "command": "npx",
      "args": ["@company/mcp-server", "--plugin-mode"],
      "cwd": "${CLAUDE_PLUGIN_ROOT}"
    }
  }
}
```

## Persistent dependencies

If the server requires `node_modules`, use `${CLAUDE_PLUGIN_DATA}` to persist them across plugin updates via a `SessionStart` hook:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "diff -q \"${CLAUDE_PLUGIN_ROOT}/package.json\" \"${CLAUDE_PLUGIN_DATA}/package.json\" >/dev/null 2>&1 || (cd \"${CLAUDE_PLUGIN_DATA}\" && cp \"${CLAUDE_PLUGIN_ROOT}/package.json\" . && npm install) || rm -f \"${CLAUDE_PLUGIN_DATA}/package.json\""
      }]
    }]
  },
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.js"],
      "env": { "NODE_PATH": "${CLAUDE_PLUGIN_DATA}/node_modules" }
    }
  }
}
```

## User-provided secrets

Declare sensitive connection strings in `userConfig` so Claude Code prompts the user:

```json
{
  "userConfig": {
    "db_url": { "description": "PostgreSQL connection string", "sensitive": true }
  },
  "mcpServers": {
    "db": {
      "command": "${CLAUDE_PLUGIN_ROOT}/bin/db-server",
      "env": { "DATABASE_URL": "${user_config.db_url}" }
    }
  }
}
```
