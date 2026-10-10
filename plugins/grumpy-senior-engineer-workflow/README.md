# grumpy-senior-engineer-workflow

A workflow toolkit for Claude Code and Codex: minimal project context,
architecture decision records, ten-section planning, and implementation
of approved plans. Both runtimes share four skills. Claude also exposes
four slash commands and prompt-based planning gates; Codex uses a planning
reminder, an agent-run structural preflight, and a Stop-hook backstop when
final-message text is available. Native Codex Plan Mode relies on the agent
running that preflight; see the [runtime limits](../../docs/plugins/grumpy-senior-engineer-workflow/codex.md#what-each-runtime-checks).
User approval remains required.

## The Problem

Project instructions (`CLAUDE.md` or `AGENTS.md`) tend to grow. Agents working
in a monorepo either re-derive "what is this subproject and what's
non-obvious about it" every session, or drag along a bloated context file
that duplicates what's already documented. Neither is cheap in tokens.

Separately, every codebase accumulates decisions nobody wrote down — why
Postgres over Mongo, why this service doesn't retry, why auth went one way
and not another. Without a record, the next person (human or agent) either
re-fights the argument or quietly reverses it without realizing a decision
was ever made.

## Guides

| Skill (Claude command) | Guide |
| --- | --- |
| `/grumpy-context` | [Project context](../../docs/plugins/grumpy-senior-engineer-workflow/context.md) — storage, operations, and examples |
| `/grumpy-adr` | [Architecture decisions](../../docs/plugins/grumpy-senior-engineer-workflow/adr.md) — lifecycle, operations, and examples |
| `/grumpy-plan` | [Planning](../../docs/plugins/grumpy-senior-engineer-workflow/plan.md) — checklist, hooks, and saving approved plans |
| `/grumpy-implement` | [Implementation](../../docs/plugins/grumpy-senior-engineer-workflow/implement.md) — building approved plans and handling deviations |

For Codex, select the corresponding skill or describe the task naturally.
See [Codex setup and compatibility](../../docs/plugins/grumpy-senior-engineer-workflow/codex.md).

## Requirements

- Claude Code or Codex with plugin and hook support.
- Bash for startup hooks; Python 3 for Codex's planning hooks.
- Git enables project-root discovery when launched from a subdirectory.
- No third-party Python packages or model credentials for Codex hooks.

## Installation

Claude Code:

```text
/plugin marketplace add omorel/ai-tools-marketplace
/plugin install grumpy-senior-engineer-workflow@olivier-vault
```

Codex installation, updates, and hook review are covered in the
[Codex guide](../../docs/plugins/grumpy-senior-engineer-workflow/codex.md).

### Companion skill availability

The planning and implementation skills consult `fastapi-resilience` for calls
outside the process. That companion skill is not yet available in `olivier-vault`
and is not bundled with Grumpy. Its addition is tracked in the
[fastapi-resilience follow-up](../../docs/follow-ups/add-fastapi-resilience.md).
When it is unavailable, the agent states that limitation and follows applicable
repository guidance without claiming to have consulted the companion.
