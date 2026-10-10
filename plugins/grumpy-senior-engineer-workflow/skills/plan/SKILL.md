---
name: plan
description: >-
  Drafts plans with ten required sections covering constraints, decisions,
  models, operations, diagrams, files, tests, size, ADRs, and documentation.
  Use proactively when asked to plan, design, scope, or architect work,
  while drafting a plan, or before presenting one for approval in Claude
  or Codex. Also handles the Claude command
  /grumpy-senior-engineer-workflow:grumpy-plan. Ends at approval and saving;
  use implement for a plan the user has already approved.
---

# Plan

A grumpy senior engineer has sat through enough "let's figure out the
details while coding" plans to know how that ends: a PR nobody can
review in one sitting, a data model that changes shape three commits
in, and a test suite that either tests nothing real or tests the config
file you just wrote. A plan's job is to make all of that visible
*before* anyone starts typing — not to be long, just to be honest about
what it doesn't know yet.

This skill doesn't tell you how to solve the problem. It tells you what
a finished plan has to show, and how to work with the user while you
get there.

## Runtime and approval

In Claude, use `EnterPlanMode`/`ExitPlanMode` when available; the existing
prompt hooks check readiness and the ten sections. In Codex, select this
plugin's `plan` skill or ask for a Grumpy plan in natural language. Use the
host's planning mode where available; do not assume Claude tool names exist.

For completed Codex plans, the entire final message is one
`<proposed_plan>...</proposed_plan>` envelope, with each tag on its own line.
Inside it, use the ten exact section names below as Markdown headings,
optionally numbered. Keep clarification replies outside this envelope.
Codex's Stop hook checks structure only when it receives the plan text;
native Plan Mode can omit that text. It cannot judge quality or prove approval.

Before presenting a completed Codex plan, run the shipped checker yourself.
Set `grumpy_plan_skill_dir` to the absolute directory containing this loaded
`SKILL.md`, using shell-safe quoting. Resolve the script from that directory;
`PLUGIN_ROOT` is not guaranteed to exist in ordinary tool commands.
Use Bash and Python 3 with the following stdin template, replacing the body
with the exact complete final plan; do not run the illustrative body literally:

```bash
python3 "$grumpy_plan_skill_dir/../../hooks/codex-plan.py" --check-plan <<'GRUMPY_PLAN'
<proposed_plan>
[Exact complete plan, including all ten sections, goes here.]
</proposed_plan>
GRUMPY_PLAN
```

Fix any reported structural errors, then rerun with the corrected text.
Any later edit requires another check before presenting. This writes no plan
file and can run in Plan Mode before approval. Skip this check for clarification
replies. If Bash, Python 3, or the checker cannot run, disclose that structural
validation was not completed; do not claim it passed. This is a skill-directed
tool call, not automatic native-hook enforcement or semantic review.

Use the runtime's question tool when available (`AskUserQuestion` in
Claude, `request_user_input` in Codex), otherwise ask in conversation.
Present the complete plan and await explicit user approval before saving
or implementing it. Hook success and leaving planning mode are not approval.

## Before drafting: is there enough to plan from?

A plan built around a guessed-at goal doesn't save anyone time — it
just moves the misunderstanding two rounds later, now dressed up with a
diagram and a file tree that make it look considered. Before drafting
(and before `EnterPlanMode` in Claude), check two things:

1. **Context** — is it reasonably clear what part of the system or
   product this touches, and why now? This can come from the request
   itself, or from what's already loaded (`AGENTS.md`, `CLAUDE.md`, `.contexts/`,
   `docs/adr/`, earlier conversation) — it doesn't have to be restated
   if it's already known.
2. **Scope** — is there at least a rough boundary of what "done" looks
   like? "Add idempotent retries to the billing publisher" has one;
   "make the billing service better" doesn't.

If either is genuinely missing, don't guess and don't start drafting —
use the available question mechanism to ask for exactly what's missing, then proceed.

Notably absent from this list: a stated design or implementation
approach. Don't demand that from the user upfront — proposing an
approach (and surfacing the forks in it) is the plan's job, not a
prerequisite for starting one. Requiring Context and Scope keeps the agent
from inventing the goal; requiring Design too would just shift the
plan's own work onto the user before it begins.

Claude's `EnterPlanMode` hook checks readiness; Codex supplies a planning
reminder. In either runtime, establish context and scope yourself.

## The ten sections

Every completed plan has all ten of these, in this order, before approval.
"None — because X" is a completely valid answer for several of them.
An absent section reads as *forgot to check*, not *doesn't apply* — the
point of the list is to make the check visible, not to pad the plan.

| # | Section | What goes there |
|---|---|---|
| 1 | **Non-negotiables** | The standing constraints this task must honor, and how the plan honors them. |
| 2 | **Decisions** | Every point with more than one reasonable approach, handed to the user — not resolved silently. |
| 3 | **Models** | Domain/data models introduced or changed, named with the project's real current names. |
| 4 | **Functions** | The operations required, one line each — no implementations yet. |
| 5 | **Diagram** | An ASCII-art sketch of the new logic: sequence, class, or state. |
| 6 | **File tree** | Only the files this plan touches, each with a one-line reason. |
| 7 | **Tests** | The specific tests worth writing, tied to real risk. |
| 8 | **Size check** | An estimate of the diff, and a split proposal if it's large. |
| 9 | **ADR check** | Whether this plan settles something worth recording — and where, not how. |
| 10 | **Documentation check** | What outside the code itself needs updating. |

### 1. Non-negotiables

Before designing anything, check what this project already requires of
every change — its applicable `AGENTS.md`/`CLAUDE.md` instructions,
`.contexts/` if the `context` skill is
in use, `docs/adr/INDEX.md` if the `adr` skill is in use. These carry
things like multi-tenancy, a security posture, a compliance rule, a
naming convention — whatever this specific codebase has already decided
it can't compromise on. Name the ones that actually bite for this task
and say how the plan honors each. If it's genuinely unclear what this
project's non-negotiables are, ask the user rather than guessing —
inventing a constraint is as bad as missing a real one.

### 2. Decisions

List every fork in the plan where more than one reasonable approach
exists — a storage choice, a protocol, a place to put a piece of logic.
For each one, give the user enough context to actually judge it (the
options, and what each one costs), then use the available question mechanism
rather than picking on their behalf. The person reading this plan is
the architect and tech lead; your job is to hand them a real choice with
real information, not to have already made the call and be looking for
a rubber stamp. If there's genuinely no fork — the approach was
unambiguous once you understood the task — say that plainly instead of
inventing a decision to fill the section.

★ Insight: "context, then the question" is the whole trick here. Asking
"Redis or Postgres for this cache?" with no setup makes the user do your
analysis for you. Explaining what each choice costs first, *then*
asking, is what actually respects their time — they're deciding, not
researching.

### 3. Models

Every domain or data model this plan introduces or changes, listed
before a single function name — a model shapes the functions that use
it, not the other way round. Use the project's real, current names.
Never carry forward a placeholder or internal codename from an earlier
phase (a proof-of-concept nickname that quietly became the production
name is a tax every future reader pays); if you're unsure what the
current name is, that's a non-negotiables question, not a guess.

### 4. Functions

The operations the plan actually requires, one line each — what it
does and why it exists, not how. If you find yourself writing more than
a sentence per function, you're implementing in the plan; stop and move
that detail to where it belongs, in the code.

### 5. Diagram

An ASCII-art sketch of the new logic — sequence, class/component, or
state, whichever one actually clarifies *this* change. See
`references/ascii-diagrams.md` for templates and guidance on picking
the right shape. A diagram that's just a box saying "does the thing"
isn't a diagram, it's decoration; if the change has no interesting flow
to show, say so instead of drawing one anyway.

### 6. File tree

Only the files this plan touches — never the whole repo — each
annotated with a short reason. Someone should be able to read this
section alone, without the rest of the plan, and know the blast radius
of what's about to change.

```
src/
  billing/
    invoice.py       # add tenant_id column handling for multi-tenant billing
    idempotency.py    # new — dedupes retried Kafka publishes
tests/
  billing/
    test_idempotency.py  # new — covers the dedup path above
```

### 7. Tests

Name the specific tests worth writing, and why each one buys real
confidence — not a coverage number. A test that only asserts a config
file contains the values you just typed into it isn't confidence, it's
an echo; skip those. If a change genuinely doesn't need new tests (a
doc fix, a rename with no behavior change), say so.

### 8. Size check

Estimate roughly how large the resulting diff will be. Past ~2000
changed lines, flag it and propose a concrete way to split the work
into smaller, independently mergeable pieces — phased by layer, by
feature slice, whatever actually divides cleanly for this change.
Finding out a PR is too big during review costs the reviewer's time and
yours; catching it here costs nothing.

### 9. ADR check

Ask whether this plan settles something that isn't already on record —
a technology choice, a new capability with real alternatives that were
passed over. If so, say which decision and point at the `adr` skill
(`/grumpy-senior-engineer-workflow:grumpy-adr new ...`) rather than
drafting the ADR inline here — this section's job is to *notice*, the
`adr` skill's job is to *record*. If nothing in this plan rises to that
bar, say so.

### 10. Documentation check

Name what needs updating outside the code itself: a README, a
project instruction line, an ADR's status flipping to `implemented`, a runbook.
"Nothing" is a fine answer when it's actually true.

## Working with the user

- **Context before the question.** Anywhere this plan asks the user to
  decide something, explain what's actually at stake first. A bare
  "A or B?" forces them to reconstruct your analysis before they can
  even answer it.
- **Plain language.** Explain the plan the way you'd explain it out
  loud to a colleague, not the way you'd write a paper. Precision
  matters more than vocabulary.
- **Small beats clever.** Prefer the design with the smaller footprint
  and the shorter files when more than one design would honestly work —
  this is a bias to apply while drafting, not just a note in the size
  check at the end.

## Saving the plan

Once the user approves the plan, write it — all ten sections,
exactly as approved — to `docs/plans/<slug>.md`, where `<slug>` is a
kebab-case cut of the task (the same convention `docs/adr/` already uses
for its own filenames). This is what makes a plan durable past the
conversation that produced it: the `implement` skill reads from this
file, and so does anyone resuming the work in a later session.

If `docs/plans/` doesn't exist yet, create it — no bootstrap step or
confirmation gate needed here; unlike `docs/adr/`, a plan file isn't a
decision record, it's a snapshot of what was just approved a moment ago
in the same turn.

Skip this only if implementation is starting in this same turn and will
finish before the conversation could plausibly be interrupted — saving
first and building second would be pure overhead there. When in doubt,
save it; a plan that outlives the session it was approved in is the
common case, not the exception.

## Companion skills

Consult companions only when relevant and available. If a referenced
skill is unavailable, say so briefly and follow applicable repository
guidance; never claim to have consulted it or invent its instructions.

- **`adr`** — see section 9. This skill notices decision-worthy moments;
  it never drafts the ADR itself.
- **`fastapi-resilience`** — when available, consult it for design guidance whenever the
  plan includes a call to anything outside the process: an HTTP call, a
  database, a gRPC stub, a broker publish (Kafka, RabbitMQ). Its
  retry/backoff/timeout patterns are the point, not the word "FastAPI"
  in its name — pull from it even in a codebase that isn't using
  FastAPI at all.
- **`implement`** — takes over once a plan is saved and approved. This
  skill's job ends at user approval and the save step above, not at the
  first line of code.
- **`humanizer` and PR/commit-convention skills** are not this skill's
  job to invoke. They trigger on their own once actual commit messages
  or PR descriptions get written, which happens after a plan is
  approved and implemented — earlier than that, there's no prose for
  them to work on yet.

## What not to do

- Don't pad a section with restated context just so it isn't empty —
  "none, because X" is a complete answer.
- Don't resolve a real fork silently to save a round-trip; ask the user.
- Don't draft an ADR inside a plan — flag it and stop, per section 9.
- Don't let the diagram or file tree drift from what the Models/
  Functions sections actually say; a plan that contradicts itself is
  worse than a plan that admits it doesn't know something yet.
- Don't treat a runtime hook as the actual quality bar or as consent.
  You remain responsible for the plan's substance and user approval.

## Worked example

> "Add idempotent Kafka publishing to the billing service so retried
> messages don't double-charge a tenant."

A plan for this would run: **Non-negotiables** — multi-tenancy and
security apply, so idempotency keys must be scoped per-tenant, not
global. **Decisions** — in-memory dedup cache vs. a persisted
idempotency table; lay out the tradeoff (survives a restart vs. extra
storage) and ask which one, rather than picking. **Models** — an
`IdempotencyRecord` (tenant-scoped key, message hash, expiry).
**Functions** — `publish_with_idempotency_key`, `has_been_published`,
`record_published`. **Diagram** — a short sequence diagram: publisher →
idempotency check → Kafka. **File tree** — the two or three files this
actually touches. **Tests** — a retried-publish-is-deduped test, a
different-tenants-same-key-are-independent test; skip testing the Kafka
client config itself. **Size check** — likely under 500 lines, no split
needed. **ADR check** — flag that "idempotency table vs. in-memory
cache" is exactly the kind of decision worth recording once the user
picks one. **Documentation check** — note the billing service's README
section on Kafka publishing needs a line about the new dedup behavior.

Once approved, this plan is saved to
`docs/plans/idempotent-kafka-publishing-billing.md` — see the
`implement` skill for how it picks up from there.
