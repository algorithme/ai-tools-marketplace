# Agents

A plugin can ship **subagents** — specialized Claude instances with their own system prompt, model, and tool restrictions. Claude invokes them automatically when a task matches their description, or users invoke them manually via `/agents`.

Upstream reference: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)

## File structure

```
plugins/my-plugin/
└── agents/
    └── security-reviewer.md
```

## Frontmatter

```yaml
---
name: security-reviewer
description: Reviews code for security vulnerabilities. Invoke when editing auth, crypto, or input handling.
model: sonnet
effort: medium
maxTurns: 20
disallowedTools: Write, Edit
isolation: worktree
---
```

| Field | Required | Notes |
|---|---|---|
| `name` | Recommended | Namespaced as `<plugin-name>:<agent-name>` in the UI. |
| `description` | Required | Claude uses this to decide when to auto-invoke the agent. |
| `model` | No | `opus`, `sonnet`, `haiku`. Defaults to the session model. |
| `effort` | No | `low`, `medium`, `high`. Controls thinking budget. |
| `maxTurns` | No | Maximum number of tool-use iterations. |
| `tools` | No | Explicit allow-list of tools (array of strings). |
| `disallowedTools` | No | Tools the agent must not use. |
| `skills` | No | Array of skill names the agent can invoke. |
| `memory` | No | Whether to load memory context. |
| `background` | No | Run the agent in the background. |
| `isolation` | No | Only `"worktree"` is supported. Runs in an isolated git worktree. |

> **Security note**: `hooks`, `mcpServers`, and `permissionMode` are **not** supported for plugin-shipped agents.

## Agent body

The body is the system prompt for the agent:

```markdown
---
name: security-reviewer
description: Reviews code for OWASP Top 10 vulnerabilities.
model: sonnet
disallowedTools: Write, Edit, Bash
---

You are a security-focused code reviewer. Your role is to:
- Identify injection vulnerabilities (SQL, command, XSS).
- Flag insecure direct object references.
- Spot hard-coded secrets or credentials.
- Check for insecure cryptography.

Be direct. Output findings in a structured list with severity (critical / high / medium / low) and a one-line fix recommendation.
```

## Custom paths

```json
{ "agents": ["./agents/", "./custom-agents/triage.md"] }
```
