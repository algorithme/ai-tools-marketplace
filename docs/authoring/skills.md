# Skills

A **skill** adds a `/command-name` shortcut to Claude Code. Skills are directories containing a `SKILL.md` file that defines the skill's prompt and metadata.

Upstream reference: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills)

## Directory structure

```
plugins/my-plugin/
└── skills/
    └── my-skill/
        ├── SKILL.md          ← required
        ├── reference.md      ← optional supporting context
        └── scripts/          ← optional helper scripts
```

## SKILL.md frontmatter

```yaml
---
description: What this skill does — shown in /plugin discover
disable-model-invocation: false   # true = no LLM call; skill runs as a pure script
name: my-skill                    # optional override; defaults to directory name
---
```

| Field | Required | Default | Notes |
|---|---|---|---|
| `description` | Recommended | — | Shown in `/plugin discover` and to Claude when auto-invoking. |
| `name` | No | directory name | Override the invocation name. Useful when the install dir name is unpredictable. |
| `disable-model-invocation` | No | `false` | Set to `true` for skills that run a fixed script without an LLM call. |

## SKILL.md body

The body is the prompt that runs when the skill is invoked. Write it as you would a user message to Claude.

```markdown
---
description: Review the selected code for bugs and security issues
---

Review the code I've selected or the recent changes in this session.

Look for:
- Potential bugs or edge cases
- Security vulnerabilities (OWASP Top 10)
- Readability improvements

Be concise. Output a bullet list with severity labels (high / medium / low).
```

## Supporting files

Files placed alongside `SKILL.md` are available to the skill at runtime:

- `reference.md` — additional context loaded automatically.
- `scripts/` — executable scripts invoked from the skill body or hooks.

Reference files can be included in the prompt using `${CLAUDE_PLUGIN_ROOT}/skills/my-skill/reference.md` in hook configurations.

## Registration

Skills are auto-discovered from `skills/` at the plugin root. To use a custom path, set `skills` in `plugin.json`:

```json
{ "skills": ["./custom/skills/", "./skills/"] }
```

## Example

```
plugins/code-review/
├── .claude-plugin/plugin.json
└── skills/
    └── review/
        └── SKILL.md
```

After installing: `/review` invokes the skill.
