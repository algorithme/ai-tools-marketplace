# Hooks

Hooks let your plugin respond to Claude Code lifecycle events — before a tool runs, after a file is written, when a session starts, and more.

Upstream reference: [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks)

## File location

```
plugins/my-plugin/
└── hooks/
    └── hooks.json
```

## hooks.json format

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format-code.sh"
          }
        ]
      }
    ]
  }
}
```

## Event reference

| Event | When |
|---|---|
| `SessionStart` | Session begins or resumes |
| `UserPromptSubmit` | Before Claude processes a prompt |
| `PreToolUse` | Before a tool call — can block it |
| `PermissionRequest` | A permission dialog appears |
| `PermissionDenied` | A tool call is denied |
| `PostToolUse` | After a tool call succeeds |
| `PostToolUseFailure` | After a tool call fails |
| `Notification` | Claude sends a notification |
| `SubagentStart` / `SubagentStop` | Subagent lifecycle |
| `TaskCreated` / `TaskCompleted` | Task lifecycle |
| `Stop` | Claude finishes responding |
| `InstructionsLoaded` | A CLAUDE.md or rules file is loaded |
| `ConfigChange` | A config file changes during session |
| `CwdChanged` | Working directory changes |
| `FileChanged` | A watched file changes on disk |
| `PreCompact` / `PostCompact` | Context compaction lifecycle |
| `SessionEnd` | Session terminates |

## Hook types

### `command` — run a shell script

```json
{
  "type": "command",
  "command": "${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
}
```

Use `${CLAUDE_PLUGIN_ROOT}` for all plugin-relative paths. The script receives the event JSON on stdin.

### `http` — POST to a URL

```json
{
  "type": "http",
  "url": "https://hooks.example.com/claude-event"
}
```

### `prompt` — evaluate with an LLM

```json
{
  "type": "prompt",
  "prompt": "Summarise this tool result: $ARGUMENTS"
}
```

### `agent` — run an agentic verifier

```json
{
  "type": "agent",
  "prompt": "Verify the written code passes security checks."
}
```

## Important rules

- Hook scripts must be **executable** (`chmod +x`).
- Always reference scripts via `${CLAUDE_PLUGIN_ROOT}`, not relative paths.
- The `matcher` field is a regex matched against the tool name.
- `PreToolUse` hooks can block a tool call by returning a non-zero exit code.

## Example: auto-format on save

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/prettier.sh"
          }
        ]
      }
    ]
  }
}
```

`scripts/prettier.sh`:

```bash
#!/usr/bin/env bash
# Reads the written file path from stdin (event JSON) and runs prettier.
FILE=$(jq -r '.tool_input.path // empty' 2>/dev/null)
[ -n "$FILE" ] && command -v prettier &>/dev/null && prettier --write "$FILE"
exit 0
```
