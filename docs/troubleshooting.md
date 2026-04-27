# Troubleshooting

## Validation errors

### `marketplace.json has JSON syntax errors`

Run `jq . .claude-plugin/marketplace.json` to pinpoint the line. Common causes:
- Trailing comma on the last element of `plugins: [...]`.
- Missing comma between plugin entries.
- Unquoted string value.

### `Plugin directory must be kebab-case`

Rename the directory to use only lowercase letters, digits, and hyphens: `my-plugin` not `MyPlugin` or `my_plugin`.

### `Plugin name must be set in plugin.json`

Add `"name": "your-plugin-name"` as the first field in `.claude-plugin/plugin.json`.

### `ajv not found` / `yq not found` / `shellcheck not found`

Install the missing tool:

```bash
# ajv-cli
npm install -g ajv-cli ajv-formats

# yq
pip install yq

# shellcheck (macOS)
brew install shellcheck
# shellcheck (Ubuntu/Debian)
sudo apt install shellcheck
```

### `YAML frontmatter failed to parse`

Open the flagged `.md` file and check the YAML block between the `---` delimiters. Common issues:
- Unquoted string containing `:` — wrap in quotes: `description: "My: plugin"`.
- Inconsistent indentation (mix of tabs and spaces).
- Missing closing `---`.

## Marketplace install issues

### `/plugin marketplace add` fails with "path not found"

Ensure you are running the command from a directory where Claude Code can resolve `omorel/ai-tools-marketplace` as a GitHub shorthand, or use the full URL:

```
/plugin marketplace add https://github.com/omorel/ai-tools-marketplace.git
```

### Plugin installed but skill/agent not appearing

1. Verify the component directory is at the **plugin root**, not inside `.claude-plugin/`:
   ```
   plugins/my-plugin/skills/   ✓
   plugins/my-plugin/.claude-plugin/skills/   ✗
   ```
2. Run `claude --debug` to see component registration logs.
3. Check that `plugin.json` does not have a conflicting `skills` path override pointing to a non-existent directory.

### Update not applied after changing plugin code

Bump the `version` in `plugin.json`. Claude Code skips re-installs when the version is unchanged.

### `claude plugin validate` returns errors in CI but script passes

The `claude plugin validate` step in CI is **informational** and non-blocking (see [adr/0003](../adr/0003-validation-and-ci.md)). Check the output: if it reports an error that `scripts/validate.sh` does not catch, open an issue or update `schemas/plugin.schema.json` to close the gap.

## Hooks not firing

1. Check the script is executable: `chmod +x ./scripts/your-hook.sh`
2. Verify the shebang: first line must be `#!/usr/bin/env bash` or `#!/bin/bash`.
3. Confirm the event name is correct (case-sensitive): `PostToolUse`, not `postToolUse`.
4. Test the script manually outside Claude Code.

## MCP server not starting

1. Check the binary path uses `${CLAUDE_PLUGIN_ROOT}`: `"command": "${CLAUDE_PLUGIN_ROOT}/bin/server"`.
2. Run `claude --debug` to see MCP initialisation errors.
3. Verify the binary is executable and exists in the plugin directory.
