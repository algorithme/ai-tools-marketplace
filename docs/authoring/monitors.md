# Monitors

**Monitors** are background watchers that arm automatically when the plugin is enabled at session start, or when a skill in the plugin is invoked.

Upstream reference: [code.claude.com/docs/en/plugins-reference#file-locations-reference](https://code.claude.com/docs/en/plugins-reference) · [Monitor tool](https://code.claude.com/docs/en/tools-reference#monitor-tool)

## File location

```
plugins/my-plugin/
└── monitors/
    └── monitors.json
```

## monitors.json format

```json
{
  "monitors": [
    {
      "command": "${CLAUDE_PLUGIN_ROOT}/scripts/watch-logs.sh",
      "description": "Watch application logs for errors"
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `command` | Yes | Shell command to run in the background. Use `${CLAUDE_PLUGIN_ROOT}`. |
| `description` | Recommended | What this monitor watches — shown in the UI. |

## Lifecycle

- Monitors are **armed at session start** when the plugin is enabled.
- They are also armed when a skill from the plugin is invoked, if not already running.
- Each monitor line written to stdout is delivered as a notification to Claude.

## Custom paths

```json
{ "monitors": "./monitors/monitors.json" }
```

## Example: error log watcher

```json
{
  "monitors": [
    {
      "command": "tail -f /var/log/myapp/error.log | grep --line-buffered ERROR",
      "description": "Stream ERROR-level log lines from myapp"
    }
  ]
}
```
