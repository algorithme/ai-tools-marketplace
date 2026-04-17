# Commands

**Commands** are skills defined as flat Markdown files rather than directories. Prefer `skills/` for new plugins — commands exist for backward compatibility.

Upstream reference: [code.claude.com/docs/en/plugins-reference#skills](https://code.claude.com/docs/en/plugins-reference)

## Structure

```
plugins/my-plugin/
└── commands/
    ├── status.md
    └── logs.md
```

Each `.md` file becomes a `/command-name` skill. The filename (without `.md`) is the command name.

## Frontmatter

Same as skills — `description` and `disable-model-invocation` are supported:

```yaml
---
description: Show the current deployment status
---

Check the deployment status and summarise what is running.
```

## When to use commands vs skills

| Use skills when… | Use commands when… |
|---|---|
| The skill has supporting files (reference.md, scripts/) | The skill is a single self-contained file |
| You want a stable `name` override in frontmatter | Simplicity is the priority |

## Custom paths

```json
{ "commands": ["./commands/", "./extra/cmd.md"] }
```

You can mix directories and individual files in the array.
