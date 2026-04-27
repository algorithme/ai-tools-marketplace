# User configuration (`userConfig`)

`userConfig` declares values that Claude Code prompts the user to provide when the plugin is first enabled. Use this instead of asking users to manually edit `settings.json`.

Upstream reference: [code.claude.com/docs/en/plugins-reference#user-configuration](https://code.claude.com/docs/en/plugins-reference)

## Declaring user config

In `plugin.json`:

```json
{
  "userConfig": {
    "api_endpoint": {
      "description": "Your team's API endpoint (e.g. https://api.example.com)",
      "sensitive": false
    },
    "api_token": {
      "description": "API authentication token",
      "sensitive": true
    }
  }
}
```

| Field | Required | Notes |
|---|---|---|
| `description` | Yes | Shown to the user in the prompt dialog. |
| `sensitive` | No (default `false`) | If `true`, stored in the system keychain. |

## Using config values

Values are substituted as `${user_config.<key>}` in:
- MCP and LSP server configs (`command`, `args`, `env`).
- Hook commands.
- Skill and agent content (non-sensitive values only).

Values are also exported as `CLAUDE_PLUGIN_OPTION_<KEY>` environment variables to hook processes and MCP subprocesses.

### Example — MCP server with a user-provided token

```json
{
  "userConfig": {
    "api_token": { "description": "API token", "sensitive": true }
  },
  "mcpServers": {
    "my-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/bin/server",
      "env": { "API_TOKEN": "${user_config.api_token}" }
    }
  }
}
```

## Storage

| Type | Storage location |
|---|---|
| Non-sensitive | `settings.json` under `pluginConfigs[<plugin-id>].options` |
| Sensitive | System keychain (or `~/.claude/.credentials.json` as fallback) |

> **Keychain limit**: the system keychain shared with OAuth tokens has an ~2 KB total limit. Keep sensitive values small (tokens, short connection strings).

## Re-prompting

To re-prompt the user for a config value, uninstall and reinstall the plugin, or remove the entry from `settings.json` manually.
