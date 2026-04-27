# Output styles

**Output styles** change how Claude formats its responses when the style is active.

Upstream reference: [code.claude.com/docs/en/plugins-reference#file-locations-reference](https://code.claude.com/docs/en/plugins-reference)

## File location

```
plugins/my-plugin/
└── output-styles/
    └── terse.md
```

## Format

Each `.md` file in `output-styles/` defines one style. The filename (without `.md`) becomes the style name.

```markdown
---
description: Terse responses — bullet points only, no prose
---

When responding, use only:
- Bullet points for lists
- Short code blocks for code
- No introductory sentences
- No trailing summaries

Be as brief as possible while remaining accurate.
```

## Frontmatter

| Field | Required | Notes |
|---|---|---|
| `description` | Recommended | Shown in the style selector UI. |

## Custom paths

```json
{ "outputStyles": ["./output-styles/", "./styles/extra.md"] }
```

## Usage

Once a style is installed, users activate it via the Claude Code style selector or by referencing it in session settings.
