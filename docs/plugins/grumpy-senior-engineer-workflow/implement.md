# Implementation

[Plugin overview](../../../plugins/grumpy-senior-engineer-workflow/README.md)

Takes an approved plan — a path under `docs/plans/`, or the one just
approved this session — and builds it, under the same guardrails it was
designed with:

- Every non-negotiable the plan named gets enforced while writing code,
  not just acknowledged.
- The file tree, models, functions, and diagram get built as approved.
  Small, obviously implied additions (an `__init__.py`, an import fix)
  proceed on their own; anything that reopens a Decision or changes
  scope stops and asks using the runtime's available question mechanism instead of getting resolved
  silently.
- Write the tests the plan named when they buy real confidence. If a
  real risk emerges that the plan missed, name it and add a test for it —
  no coverage padding, no testing configuration for its own sake.
- The running diff is watched against the plan's own size estimate, not
  just checked once at the end.
- The plan's ADR check gets followed through: a flagged decision gets
  offered to the `adr` skill to record for real once it's actually
  shipping, and an ADR that just shipped gets offered a status flip from
  `accepted` to `implemented` via that same skill.
- The documentation updates the plan named actually get made, not left
  as a note.

## Usage

Claude command example (Codex uses skill selection or natural language):

```text
/grumpy-senior-engineer-workflow:grumpy-implement docs/plans/idempotent-kafka-publishing-billing.md
```

It also triggers from plain language once a plan has sign-off — "go
ahead and build that" or "implement this" right after approving a plan
works without the slash command or a file path.
Approval comes from the user, independently of plan formatting or hook results.

## How It Works

- **[`skills/implement/SKILL.md`](../../../plugins/grumpy-senior-engineer-workflow/skills/implement/SKILL.md)** is the single source of truth for
  turning an approved plan into code: how to locate the plan (a given
  path, or the one just approved this session), how each of the ten
  plan sections becomes an actual build-time obligation, and the line
  between a deviation that can proceed and one that has to stop and ask.
  It has no dedicated implementation hook: select the skill, use natural
  language, or invoke the Claude `/grumpy-implement` command.
- **[`commands/grumpy-implement.md`](../../../plugins/grumpy-senior-engineer-workflow/commands/grumpy-implement.md)** is a thin dispatcher for the
  explicit `/grumpy-senior-engineer-workflow:grumpy-implement` command —
  it resolves the plan-file argument (or falls back to the session's
  just-approved plan) and defers everything else to the skill.
