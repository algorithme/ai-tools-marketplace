# Channels

**Channels** let a plugin declare a message source (e.g. Telegram, Slack, Discord) that injects content directly into the Claude Code conversation. Each channel binds to an MCP server provided by the plugin.

Upstream reference: [code.claude.com/docs/en/plugins-reference#channels](https://code.claude.com/docs/en/plugins-reference)

## Declaring a channel

In `plugin.json`:

```json
{
  "channels": [
    {
      "server": "telegram",
      "userConfig": {
        "bot_token": {
          "description": "Telegram bot token (from @BotFather)",
          "sensitive": true
        },
        "owner_id": {
          "description": "Your Telegram user ID (numeric)",
          "sensitive": false
        }
      }
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `server` | Yes | Must match a key in the plugin's `mcpServers`. |
| `userConfig` | No | Per-channel config values — same schema as top-level `userConfig`. |

## How it works

```
Telegram / Slack / Discord
        │  (message received by bot)
        ▼
  MCP server (bundled in plugin)
        │  (MCP tool call → inject into conversation)
        ▼
  Claude Code session
        │
        ▼
  Claude processes the message
```

The MCP server must implement the MCP channel protocol so that incoming messages are injected into the active Claude Code session.

## Full example — Telegram plugin

```json
{
  "name": "telegram-channel",
  "version": "1.0.0",
  "channels": [
    {
      "server": "telegram",
      "userConfig": {
        "bot_token": { "description": "Telegram bot token", "sensitive": true },
        "owner_id":  { "description": "Telegram user ID", "sensitive": false }
      }
    }
  ],
  "mcpServers": {
    "telegram": {
      "command": "${CLAUDE_PLUGIN_ROOT}/bin/telegram-mcp",
      "env": {
        "BOT_TOKEN": "${user_config.bot_token}",
        "OWNER_ID":  "${user_config.owner_id}"
      }
    }
  }
}
```

## Channel access control

The MCP server is responsible for authenticating and authorising which users/channels can inject messages. Claude Code does not add additional access control beyond what the MCP server enforces.
