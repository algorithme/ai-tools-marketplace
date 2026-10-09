---
name: implement
description: >-
  Carries out an approved plan — the ten-section plan produced by the
  `plan` skill, saved to docs/plans/ — turning it into actual code,
  tests, and documentation updates, under the same guardrails the plan
  itself was built with: non-negotiables get enforced (not just noted),
  the file tree and diagram get followed, only tests that buy real
  confidence get written, the running diff gets watched against the
  plan's own size estimate, and any real fork the plan didn't already
  resolve pauses for the user instead of getting picked silently. Use
  this PROACTIVELY whenever the user says "implement this plan", "let's
  build it", "go ahead and code this up", "start on <plan file>", hands
  over a path under docs/plans/, or asks to proceed right after a plan
  was just approved via ExitPlanMode. Also triggers on the explicit
  slash command /grumpy-senior-engineer-workflow:grumpy-implement. Do
  not trigger while a plan is still being drafted or revised — that is
  the `plan` skill's job; this skill only starts once a plan already
  has sign-off.
---

# Implement

A grumpy senior engineer has watched a carefully reviewed plan turn into
a diff that resembles it only vaguely — a file that wasn't on the list,
one function that quietly became three, a test that got dropped because
it seemed obvious at the time. The plan spent the reviewer's trust once;
this skill's job is to spend it honestly, by building what was actually
approved and saying out loud the moment reality wants something
different.

This skill doesn't design anything — that already happened in `plan`.
It executes, and it treats every one of the plan's ten sections as a
promise to keep, not a historical artifact to skim past on the way to
writing code.

## Finding the plan to implement

- Invoked with a path (`/grumpy-senior-engineer-workflow:grumpy-implement
  docs/plans/<file>.md`) — read that file.
- Invoked with no path, and a plan was drafted and approved via
  `ExitPlanMode` earlier in this same conversation — use that plan
  directly, whether or not it has been saved to `docs/plans/` yet.
- Invoked with no path and no plan approved this session — ask which
  plan to implement rather than guessing at one from earlier
  conversation.

Once you have the plan, confirm it actually carries the `plan` skill's
ten sections with real content. A plan missing pieces was never really
approved — either the `ExitPlanMode` gate was bypassed, or the file
predates this convention. Say plainly which sections are missing or
empty and ask whether to fill them in now or proceed with what's there;
don't silently build from a plan you can't fully account for.

If the plan only lives in this conversation and the build is going to
outlast the current turn, save it to `docs/plans/<slug>.md` first — see
the `plan` skill's "Saving the plan" section. The two skills share this
convention so a plan is never only as durable as the context window it
was approved in.

## Executing the ten sections

### 1. Non-negotiables
Enforce them, don't just re-read them. If something you're about to
write would violate one, stop before you write it — a non-negotiable
was named unconditional at plan time, so running into one isn't a
deviation in the sense used below, it's a bug in what you were about to
do.

### 2. Decisions
`plan` already put every fork it recognized in front of the user. Any
*new* fork discovered while building — the two functions the plan
listed separately turn out to need to be atomic, the library the plan
assumed doesn't actually support the approach — gets the same
treatment: explain what's actually at stake, then ask with
`AskUserQuestion`. Don't resolve it yourself because stopping feels like
friction; see "Handling deviations" below for where the line actually
sits.

### 3. Models
Build them with the exact names the plan used. If the codebase still
carries an old or internal name the plan's Models section didn't
inherit, that's worth a one-line flag, not a silent rename and not a
silent adoption of the stale name either.

### 4. Functions
Implement what's named. If one turns out to need splitting, merging, or
turns out unnecessary once you're actually writing it, that's a
deviation — see below, don't just quietly do the other thing.

### 5. Diagram
The diagram is the plan's source of truth for control flow. If the code
you're writing doesn't match it, one of the two is wrong — reconcile
before continuing rather than letting them silently drift apart.

### 6. File tree
Build exactly this set of files. A small, obviously implied addition (an
`__init__.py` a new package needs, an import fix, a barrel export) can
proceed without a pause. A file the plan didn't mention because a design
assumption turned out wrong is a real deviation.

### 7. Tests
Write the tests the plan named, and only the ones that earn their
place. A test that just confirms a value you typed five minutes ago into
the same file isn't confidence, it's an echo — skip it even if it would
pad coverage, and skip testing configuration for its own sake. If,
mid-build, you spot a real risk the plan's Tests section missed, name it
and add a test for it; the plan not anticipating a risk isn't a reason
to leave it uncovered either.

### 8. Size check
Watch the running diff as you build, not just once at the end. If it's
heading past the plan's own estimate — or past roughly 2000 changed
lines regardless of what the plan guessed — stop where you are and
propose a split, the same way the plan would have if it had seen this
coming.

### 9. ADR check
Two separate moments, not one:

- **Before you start** — re-check `docs/adr/INDEX.md` (via the `adr`
  skill) for anything relevant that landed since the plan was drafted. A
  plan approved two weeks ago can be implementing against a decision
  that's since been superseded.
- **If the plan flagged something as ADR-worthy** — the decision is
  about to actually ship, which is exactly when it's worth recording for
  real. Offer to draft it now via the `adr` skill (`new`), before or
  alongside the build, rather than waiting until afterward when the
  reasoning is fresher in the plan than it will be in anyone's memory.
- **Once the build is done** and an ADR (existing or just recorded)
  reflects a decision that just shipped, offer to move it from
  `accepted` to `implemented` via the `adr` skill's `implement`
  operation. This skill writes the code; `adr` is still the only thing
  that ever touches `docs/adr/`.

### 10. Documentation check
Actually make the updates the plan named — the README line, the
runbook, the `CLAUDE.md` pointer — as part of finishing, not as a TODO
left for later. "Named in the plan" and "done" should end up describing
the same list.

## Handling deviations

A plan is a promise about intent, not a contract that predicted every
line of code before it was written. Surprises during a build come in
two kinds, and they don't deserve the same response:

- **Small and obviously implied by what's already approved** — proceed,
  and mention it in passing when you report back. Don't stop for it.
- **A real fork** — anything that changes scope, reopens a Decision, or
  adds, removes, or reshapes a Model/Function/file the plan's rationale
  doesn't cover. Stop. Explain what changed and why, in plain terms —
  the same context-before-the-question rule `plan` uses — then ask with
  `AskUserQuestion`. The user approved a specific shape; building past
  it without asking spends trust the *plan* earned, not trust this
  skill has on its own.

## Comments, while writing the code

Comment classes and functions with what they're for and how to use
them — not the logic inside. The full reasoning already lives in the
plan, an ADR, or whatever they point to; a comment that restates it
inline just gives that reasoning a second place to go stale.

## Before calling it done

Run whatever the Tests section named and confirm it actually passes —
don't report a test as written without having run it once. For anything
a person would directly interact with (a UI, a CLI, an endpoint),
exercise it yourself if the environment allows, the same way you would
before telling a colleague it works. If you can't run it here, say so
plainly rather than reporting success you didn't check.

## Companion skills

- **`adr`** — see section 9. Both directions (recording a decision that's
  about to ship, and flipping `accepted` → `implemented` once it has)
  happen from inside this skill's flow, but only the `adr` skill itself
  ever writes to `docs/adr/`.
- **`fastapi-resilience`** — consult it for any code this plan adds that
  calls outside the process: HTTP, a database, gRPC, a broker (Kafka,
  RabbitMQ). Its retry/backoff/timeout patterns apply regardless of
  whether the codebase uses FastAPI at all.
- **`context`** — if this build lands in an unfamiliar monorepo
  subproject, its `.contexts/<name>.md`, if one exists, is worth a look
  before you start, same as it would be for any work there.
- **`humanizer`** and the commit/PR-convention skills aren't this
  skill's job to invoke — they trigger on their own once an actual
  commit message or PR description is being written, which happens
  after the code this skill produces exists, not during it.

## What not to do

- Don't build from a plan you haven't confirmed still has all ten
  sections with real content — a hollow section didn't actually get
  approved, it got skipped.
- Don't silently expand the file tree, rename a model, or drop/add a
  test to route around asking — see "Handling deviations."
- Don't draft or write to `docs/adr/` yourself; flag it and hand off to
  the `adr` skill, per section 9.
- Don't narrate implementation logic in code comments — that duplicates
  the plan or the ADR and drifts from it the moment either one changes.
- Don't report a test suite as passing, or a feature as working,
  without having actually run it.

## Worked example

Continuing the `plan` skill's own worked example — idempotent Kafka
publishing for billing, approved and saved to
`docs/plans/idempotent-kafka-publishing-billing.md`:

```
/grumpy-senior-engineer-workflow:grumpy-implement docs/plans/idempotent-kafka-publishing-billing.md
```

Confirms the file still has all ten sections. The plan's ADR check
flagged "idempotency table vs. in-memory cache" as decision-worthy — the
decision is now actually shipping, so this is the moment to record it
for real: offers to draft it via the `adr` skill, gets it written as
`docs/adr/0006-persist-idempotency-keys-in-a-table.md` with `status:
accepted`. Builds `billing/idempotency.py` with the `IdempotencyRecord`
model and the three named functions, wires the call into
`billing/invoice.py`, matching the plan's file tree and sequence diagram
exactly. Partway through, realizes `has_been_published` and
`record_published` being two separate calls creates a race under
concurrent retries — a real fork the plan didn't anticipate, so it
stops, explains the race and the two ways to close it (a single atomic
upsert vs. a short-lived lock), and asks rather than picking. Writes
only the two tests the plan named — nothing about testing the Kafka
client config, exactly as the plan said not to. Updates the billing
README's Kafka section per the Documentation check. Final diff: about
340 lines, comfortably under the plan's estimate, no split needed. Runs
the new tests and confirms they pass before reporting back. Offers to
flip ADR-0006 from `accepted` to `implemented` via the `adr` skill now
that it has actually shipped. The eventual PR description is left to the
`humanizer` and PR-convention skills once that text actually gets
written.
