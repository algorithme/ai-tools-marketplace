# Project context

[Plugin overview](../../../plugins/grumpy-senior-engineer-workflow/README.md)

`grumpy-senior-engineer-workflow` maintains `.contexts/` at the project root:

```
project_root/.contexts/
  index.md          # root project context + manifest of subprojects
  <subproject>.md   # one file per monorepo subproject
```

Each context body is capped at **500 characters** and is checked against
the root `CLAUDE.md` plus nested `CLAUDE.md` files within the target's
directory tree. Sibling subprojects are excluded for a subproject context.
It stores only the delta an agent couldn't get from those files.

Four operations, available as a slash command or triggered from natural
language:

| Operation | Effect |
|---|---|
| `get` | Read the current context (root, or a named subproject) |
| `set` / `reset` | Replace a context wholesale |
| `improve` / `update` | Merge new details into the existing context, compressing to stay under 500 chars |
| `add-sub` | Register a new subproject context |

A `SessionStart` hook loads `.contexts/index.md` automatically at the start
of every session, so agents start already oriented instead of asking.

## Usage

```
/grumpy-senior-engineer-workflow:grumpy-context set root this is a monorepo: FastAPI api-service + React frontend, shared Postgres, deploys via infra/ Terraform
/grumpy-senior-engineer-workflow:grumpy-context add-sub api-service auth is legacy, being replaced by svc-auth-v2, don't extend it
/grumpy-senior-engineer-workflow:grumpy-context improve api-service billing retries now use idempotency keys
/grumpy-senior-engineer-workflow:grumpy-context get frontend
```

It also triggers from plain language — "what's the context for the frontend
subproject?" or "update the project context, we moved to Postgres" work
without typing the slash command.

## How It Works

- **[`skills/context/SKILL.md`](../../../plugins/grumpy-senior-engineer-workflow/skills/context/SKILL.md)** is the single source of truth: file layout,
  the 500-character limit, the `CLAUDE.md` dedup rule, and the exact
  behavior of each operation. It auto-triggers on context-management intent.
- **[`commands/grumpy-context.md`](../../../plugins/grumpy-senior-engineer-workflow/commands/grumpy-context.md)** is a thin dispatcher for the explicit
  `/grumpy-senior-engineer-workflow:grumpy-context` command — it parses
  arguments and defers to the skill's rules rather than duplicating them.
- **[`hooks/load-context.sh`](../../../plugins/grumpy-senior-engineer-workflow/hooks/load-context.sh)** runs on `SessionStart` and prints
  `.contexts/index.md` (if present) into the session's context. Missing or
  absent `.contexts/` never blocks a session.
