# grumpy-senior-engineer-workflow

A workflow toolkit for driving AI coding agents safely. It ships four
tools: `/grumpy-context`, a minimal per-subproject context store that
keeps agents oriented without turning into a second `CLAUDE.md`;
`/grumpy-adr`, an architecture-decision-record lifecycle that keeps
agents from re-litigating or silently reversing decisions that were
already made; `/grumpy-plan`, a required checklist for any Plan-mode
deliverable, enforced by a hook so a plan missing pieces never reaches
you; and `/grumpy-implement`, which builds an approved plan under the
same guardrails it was designed with, instead of drifting from it one
quiet decision at a time.

## The Problem

`CLAUDE.md` is human-facing documentation and tends to grow. Agents working
in a monorepo either re-derive "what is this subproject and what's
non-obvious about it" every session, or drag along a bloated context file
that duplicates what's already documented. Neither is cheap in tokens.

Separately, every codebase accumulates decisions nobody wrote down — why
Postgres over Mongo, why this service doesn't retry, why auth went one way
and not another. Without a record, the next person (human or agent) either
re-fights the argument or quietly reverses it without realizing a decision
was ever made.

## Guides

| Tool | Guide |
| --- | --- |
| `/grumpy-context` | [Project context](../../docs/plugins/grumpy-senior-engineer-workflow/context.md) — storage, operations, and examples |
| `/grumpy-adr` | [Architecture decisions](../../docs/plugins/grumpy-senior-engineer-workflow/adr.md) — lifecycle, operations, and examples |
| `/grumpy-plan` | [Planning](../../docs/plugins/grumpy-senior-engineer-workflow/plan.md) — checklist, hooks, and saving approved plans |
| `/grumpy-implement` | [Implementation](../../docs/plugins/grumpy-senior-engineer-workflow/implement.md) — building approved plans and handling deviations |

## Requirements

- None beyond the base Claude Code plugin runtime — no external tools or
  dependencies.

## Installation

```bash
/plugin marketplace add omorel/ai-tools-marketplace
/plugin install grumpy-senior-engineer-workflow@olivier-vault
```

### Companion skill availability

The planning and implementation skills consult `fastapi-resilience` for calls
outside the process. That companion skill is not yet available in `olivier-vault`
and is not bundled with Grumpy. Its addition is tracked in the
[fastapi-resilience follow-up](../../docs/follow-ups/add-fastapi-resilience.md).
The existing companion references are preserved for that future addition.
