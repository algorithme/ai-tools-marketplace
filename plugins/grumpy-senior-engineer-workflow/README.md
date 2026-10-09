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

## What It Does

### `/grumpy-context`

`grumpy-senior-engineer-workflow` maintains `.contexts/` at the project root:

```
project_root/.contexts/
  index.md          # root project context + manifest of subprojects
  <subproject>.md   # one file per monorepo subproject
```

Each context body is capped at **500 characters** and is checked against
every `CLAUDE.md` in the repo (root and nested) so it never repeats what's
already documented there — it stores only the delta an agent couldn't get
elsewhere.

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

### `/grumpy-adr`

`grumpy-senior-engineer-workflow` also maintains `docs/adr/` at the
project root:

```text
project_root/docs/adr/
  INDEX.md                 # generated — never hand-edit
  templates/
    capability-adr.md
    technology-adr.md
  0001-<slug>.md
  0002-<slug>.md
```

Every ADR is drafted, presented, and only written to disk once approved —
nothing is created on a hunch. Each one carries a TL;DR (for humans
skimming the index) and an Agent guidance field (a direct instruction for
what an agent should do differently because the decision exists), on top
of the usual Context/Decision/Consequences shape. Decisions move through a
status lifecycle as they mature:

```text
proposed -> accepted -> implemented -> superseded
                     \-> deprecated       (from any non-terminal state)
```

Nine operations, available as a slash command or triggered from natural
language:

| Operation | Effect |
| --- | --- |
| `new` | Draft and, on approval, record a new ADR |
| `show` | Read a past decision by number or keyword |
| `list` | Print the index, optionally filtered |
| `accept` | `proposed` -> `accepted` |
| `implement` | `accepted` -> `implemented` |
| `supersede` | Draft a replacement ADR and link it to the one it replaces |
| `deprecate` | Retire an ADR with no successor |
| `audit` | Lint numbering, index sync, and status consistency |
| `bootstrap` | Scaffold `docs/adr/` in a repo that doesn't have it yet |

A `SessionStart` hook prints a one-line pointer ("N ADRs recorded, see
docs/adr/INDEX.md") when the index exists, rather than the full index —
unlike `.contexts/`, it has no size cap and can grow past what's worth
loading into every session.

### `/grumpy-plan`

Every Plan-mode deliverable must contain ten sections, in order, even
when a given one is honestly "none":

| # | Section | # | Section |
| --- | --- | --- | --- |
| 1 | Non-negotiables | 6 | File tree |
| 2 | Decisions | 7 | Tests |
| 3 | Models | 8 | Size check |
| 4 | Functions | 9 | ADR check |
| 5 | Diagram | 10 | Documentation check |

Before any of that, the plan needs to be built on something real, not a
guessed-at goal — see "Before drafting" in the skill. Three `PreToolUse`
hooks enforce all of this without depending on the skill happening to
auto-trigger:

- On `EnterPlanMode`, a nudge reminds Claude to apply the checklist
  before it starts drafting, and a gate **denies** the tool call — sending
  Claude to ask the user via `AskUserQuestion` first — if the task itself
  lacks basic Context (what this touches, and why) or Scope (what "done"
  looks like). A missing design/approach preference is *not* grounds for
  denial; proposing one is the plan's job.
- On `ExitPlanMode`, a gate reads the drafted plan and **denies** the
  tool call — sending Claude back to fix the plan — if any section is
  missing or hollow. The user never sees an incomplete plan.

Once approved, the plan is saved to `docs/plans/<slug>.md` so it
outlives the conversation that produced it.

### `/grumpy-implement`

Takes an approved plan — a path under `docs/plans/`, or the one just
approved this session — and builds it, under the same guardrails it was
designed with:

- Every non-negotiable the plan named gets enforced while writing code,
  not just acknowledged.
- The file tree, models, functions, and diagram get built as approved.
  Small, obviously implied additions (an `__init__.py`, an import fix)
  proceed on their own; anything that reopens a Decision or changes
  scope stops and asks via `AskUserQuestion` instead of getting resolved
  silently.
- Only the tests the plan named get written, and only if they'd buy
  real confidence — no coverage padding, no testing configuration for
  its own sake.
- The running diff is watched against the plan's own size estimate, not
  just checked once at the end.
- The plan's ADR check gets followed through: a flagged decision gets
  offered to the `adr` skill to record for real once it's actually
  shipping, and an ADR that just shipped gets offered a status flip from
  `accepted` to `implemented` via that same skill.
- The documentation updates the plan named actually get made, not left
  as a note.

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

```text
/grumpy-senior-engineer-workflow:grumpy-adr new we decided to use Postgres instead of Mongo for billing, we need cross-table transactions
/grumpy-senior-engineer-workflow:grumpy-adr show 0004
/grumpy-senior-engineer-workflow:grumpy-adr supersede 0004 moving billing to CockroachDB for multi-region writes
/grumpy-senior-engineer-workflow:grumpy-adr audit
```

It also triggers from plain language — "why did we choose Postgres for
billing?" or "let's record this decision" work without the slash command.

```text
/grumpy-senior-engineer-workflow:grumpy-plan add idempotent Kafka publishing to the billing service so retried messages don't double-charge a tenant
```

It also triggers from plain language — "how should we approach adding
dark mode?" or simply asking for something non-trivial enough that
Claude would enter Plan Mode on its own works without the slash command.

```text
/grumpy-senior-engineer-workflow:grumpy-implement docs/plans/idempotent-kafka-publishing-billing.md
```

It also triggers from plain language once a plan has sign-off — "go
ahead and build that" or "implement this" right after approving a plan
works without the slash command or a file path.

## How It Works

- **`skills/context/SKILL.md`** is the single source of truth: file layout,
  the 500-character limit, the `CLAUDE.md` dedup rule, and the exact
  behavior of each operation. It auto-triggers on context-management intent.
- **`commands/grumpy-context.md`** is a thin dispatcher for the explicit
  `/grumpy-senior-engineer-workflow:grumpy-context` command — it parses
  arguments and defers to the skill's rules rather than duplicating them.
- **`hooks/load-context.sh`** runs on `SessionStart` and prints
  `.contexts/index.md` (if present) into the session's context. Missing or
  absent `.contexts/` never blocks a session.
- **`skills/adr/SKILL.md`** is the single source of truth for the ADR
  lifecycle: templates, numbering, the approval gate, the status machine,
  and the audit checks. Its `assets/templates/` holds the actual
  capability/technology templates and the empty `INDEX.md` shape used by
  `bootstrap`.
- **`commands/grumpy-adr.md`** is a thin dispatcher for the explicit
  `/grumpy-senior-engineer-workflow:grumpy-adr` command, same pattern as
  `commands/grumpy-context.md`.
- **`hooks/load-adr-pointer.sh`** runs on `SessionStart` and prints a
  one-line pointer to `docs/adr/INDEX.md` when it exists.
- **`skills/plan/SKILL.md`** is the single source of truth for the ten
  required plan sections and how to work with the user while drafting.
  `skills/plan/references/ascii-diagrams.md` holds sequence/class/state
  diagram templates for section 5.
- **`commands/grumpy-plan.md`** is a thin dispatcher for the explicit
  `/grumpy-senior-engineer-workflow:grumpy-plan` command, same pattern
  as the other two commands.
- **`hooks/nudge-enter-plan.sh`** runs on `PreToolUse` for
  `EnterPlanMode` and always allows — it only adds a reminder message
  so the checklist is in mind before drafting starts. It runs alongside
  (not instead of) the gate below — both are registered under the same
  `EnterPlanMode` matcher in `hooks.json`.
- The `EnterPlanMode` **gate** and the `ExitPlanMode` **gate** are both
  `prompt`-type hooks defined inline in `hooks.json` (no script file).
  The entry gate reads the transcript for the user's request and denies
  the tool call if it lacks basic Context or Scope (see "Before
  drafting" in the skill). The exit gate reads the transcript for the
  drafted plan and denies the tool call if any of the ten sections is
  missing or hollow.
- **`skills/implement/SKILL.md`** is the single source of truth for
  turning an approved plan into code: how to locate the plan (a given
  path, or the one just approved this session), how each of the ten
  plan sections becomes an actual build-time obligation, and the line
  between a deviation that can proceed and one that has to stop and ask.
  Unlike the other three tools, it has no dedicated hook — it relies on
  its description and the `/grumpy-implement` command to trigger, since
  there's no single tool call (like `EnterPlanMode`/`ExitPlanMode`) to
  gate the start or end of a build against.
- **`commands/grumpy-implement.md`** is a thin dispatcher for the
  explicit `/grumpy-senior-engineer-workflow:grumpy-implement` command —
  it resolves the plan-file argument (or falls back to the session's
  just-approved plan) and defers everything else to the skill.
