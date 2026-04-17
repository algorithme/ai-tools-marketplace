# Executables (`bin/`)

Files placed in `bin/` are added to the `PATH` for every Bash tool call while the plugin is enabled. This lets you ship CLI helpers that Claude (or hook scripts) can invoke by name.

Upstream reference: [code.claude.com/docs/en/plugins-reference#file-locations-reference](https://code.claude.com/docs/en/plugins-reference)

## File location

```
plugins/my-plugin/
└── bin/
    └── my-tool        ← must be executable (chmod +x)
```

## Rules

- Files must be **executable** (`chmod +x`). `scripts/validate.sh` checks this via shellcheck.
- Files can be any executable format: shell script, Python, compiled binary.
- The `bin/` directory is at the plugin root (not inside `.claude-plugin/`).

## Example: shell helper

`bin/greet`:

```bash
#!/usr/bin/env bash
echo "Hello from my-plugin! args: $*"
```

```bash
chmod +x bin/greet
```

After install, from any Bash tool call:

```bash
greet --name world
# → Hello from my-plugin! args: --name world
```

## Referencing from hooks

You can also invoke `bin/` executables from hooks using `${CLAUDE_PLUGIN_ROOT}/bin/my-tool`:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PLUGIN_ROOT}/bin/my-tool"
      }]
    }]
  }
}
```

## Scope

`bin/` additions to `PATH` are scoped to the plugin's session. They do not persist after Claude Code exits.
