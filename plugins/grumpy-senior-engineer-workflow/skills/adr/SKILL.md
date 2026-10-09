---
name: adr
description: >-
  Records and maintains Architecture Decision Records (ADRs) under
  docs/adr/, so agents and developers know why the codebase is shaped
  the way it is instead of re-litigating settled decisions. Covers the
  full lifecycle: draft, approve, number, index, then move through
  accepted, implemented, superseded, or deprecated. Use this PROACTIVELY whenever the user says
  "let's record this decision" or "ADR this"; explicitly settles on one
  option over another ("we decided to use X instead of Y", "going with X
  because...", "the reason we chose X over Y is..."); asks "why did we
  choose X?" or "why does this use X?"; or wants to supersede, deprecate,
  or audit past decisions. Also triggers on the explicit slash command
  /grumpy-senior-engineer-workflow:grumpy-adr. Do not trigger on a technology
  merely being mentioned, or on live brainstorming that hasn't settled on
  a conclusion yet — this skill records decisions, not deliberation.
---

# Architecture Decision Records (ADR)

A grumpy senior engineer has sat through the same argument three times
because nobody wrote down why the last one ended the way it did. An ADR
is the paper trail: what was decided, why, what else was on the table,
and what it costs. Without one, the next person — human or agent —
either re-fights the argument from scratch or, worse, quietly reverses it
without realizing a decision was ever made.

This skill doesn't stop a bad decision from being made. It makes sure a
good one gets remembered, and it will say so out loud — by ADR number —
when what you're about to do runs straight into one.

## Storage layout

```
project_root/docs/adr/
  INDEX.md                 # generated — never hand-edit, always regenerate
  templates/
    capability-adr.md
    technology-adr.md
  0001-<slug>.md
  0002-<slug>.md
  ...
```

Numbers are 4-digit, contiguous from `0001`, and assigned only at write
time — see **Numbering**, below, for why. `<slug>` is a kebab-case cut of
the title.

## Two shapes of decision

Most ADRs are one of two things, and the template differs accordingly:

- **Technology ADR** — picks *how*, among named alternatives, for
  something that has no new user-facing effect (Postgres over MongoDB,
  REST over GraphQL, tenacity over hand-rolled retries).
- **Capability ADR** — decides *what* the system will do that it didn't
  before, scoped by user stories and testable acceptance criteria
  (multi-tenant billing, a public webhook API).

If it's genuinely ambiguous, default to technology — most decisions made
mid-codebase are "how," not "what."

Full templates live in `assets/templates/capability-adr.md` and
`assets/templates/technology-adr.md` — read the matching one before
drafting. Both share this frontmatter:

| Field | Meaning |
|---|---|
| `adr` | Integer, must equal the filename's number |
| `title` | Short, specific — not "Database choice," but "Use Postgres instead of MongoDB for primary storage" |
| `type` | `capability` or `technology` |
| `status` | `proposed` \| `accepted` \| `implemented` \| `superseded` \| `deprecated` |
| `date` | Date the decision was made (not the date it's typed up, if different) |
| `deciders` | Who actually made the call |
| `supersedes` / `superseded-by` | ADR number, when applicable |
| `depends-on` | Other ADR numbers this one assumes, if any |
| `tags` | Free-form, optional |

And both share these sections, on top of the type-specific middle:

- **TL;DR** — one or two sentences, before anything else. Someone
  skimming a backlog of forty ADRs should know from this line alone
  whether it's relevant to what they're doing, without reading Context or
  Consequences first.
- **Consequences** (Positive / Negative / Risks) — every decision has a
  cost, not just technology trade-offs. A capability decision still
  incurs maintenance burden, complexity, or things that get harder once
  it ships; say so here rather than letting Acceptance criteria imply the
  decision was free.
- **Agent guidance** — one or two sentences telling an agent what to do
  *differently* because this ADR exists (see below).
- **References**, **Revision History** — same as any changelog.

★ Insight: TL;DR and Agent guidance solve two different readers' problems.
TL;DR is for a human scanning the index fast. Agent guidance is for the
model reading the full record — it converts "here is some background" into
"here is the specific behavior expected of you," which is what actually
changes what an agent does. Loading a document into context shifts the
odds; a direct behavioral instruction shifts them further.

## What this means for you, day to day

1. **Retrieve before changing.** Before touching something architecturally
   significant, skim `docs/adr/INDEX.md` for anything relevant.
2. **Surface conflicts, don't silently resolve them.** If what's being
   asked conflicts with a non-terminal ADR, say so by number — "this runs
   against ADR-0007, which chose X for Y reason" — and let the user
   decide. Don't quietly comply and don't quietly enforce the old
   decision either; the point is to surface it, not to overrule anyone.
3. **Offer to draft the missing record, don't invent one.** If you're
   implementing something that clearly reflects an unrecorded decision,
   say so and offer to record it. Never create the file without approval
   — this is advisory, not an enforcement gate, and the ADR log is only
   trustworthy if every entry reflects a decision someone actually signed
   off on.

## Capturing a new ADR

Use the runtime's question tool when available, otherwise ask in conversation.
Approval means the user's confirmation of the complete draft, regardless of
runtime; a successful hook or an approved implementation plan alone does not
approve an unseen ADR draft. Reuse confirmation already given for that draft
and its bootstrap rather than requesting it again.

1. **Recognize a real decision moment** — see the description's trigger
   list. If the conversation is still exploring options with no
   conclusion, don't draft anything yet; wait for a conclusion, or ask
   whether there is one.
2. **Gather the substance in conversation** — context, the decision (or
   capability), the alternatives and why each was passed over,
   consequences. Don't hand the user a form; extract this from what
   they've already said and ask only for genuine gaps.
3. **Pick the template** (technology vs capability — ask if unclear).
4. **Draft the whole thing**, TL;DR and Agent guidance included, but do
   not write it to disk.
5. **Present the draft and ask two things**: is it accurate, and is the
   decision actually final or still open? The answer to the second
   question sets the initial status — `accepted` if final, `proposed` if
   real open questions remain. Most decisions captured this way ("we
   decided to...") are already final; don't force everything through a
   `proposed` stage it doesn't need.
6. **On approval, write it**:
   - If `docs/adr/` doesn't exist yet, run **Bootstrap** first (still
     asking before creating anything — see below).
   - Re-scan `docs/adr/` for the highest existing number and take the
     next one, immediately before writing (not earlier).
   - Write `docs/adr/NNNN-<slug>.md`.
   - Regenerate `docs/adr/INDEX.md` — add or re-sort the row; never
     hand-append without checking the rest of the table still matches
     reality.
7. **On rejection or requested changes**, revise and re-present. If the
   user declines outright, discard it — nothing is written, no number is
   spent.

★ Insight: numbers are assigned only at write time, immediately before
the file is created, rather than reserved up front. This is the cheapest
available defense against two decisions grabbing the same number — there
is no coordination mechanism between agents or sessions here, so the best
this skill can do is shrink the window where a collision could happen,
and let `audit` (below) catch it if one still does.

## Reading existing ADRs

On "why did we choose X" / "why does this use X":

1. Check `docs/adr/INDEX.md` exists. If not, say so — don't guess at an
   answer — and offer to record one instead if the reasoning is available
   in this conversation.
2. Search the index table and filenames/content for the keyword.
3. Found: answer with **TL;DR + Decision (or Capability statement) +
   current status** — not the whole file — unless more detail is asked
   for.
4. Not found: say so plainly, and offer to record it now if the
   conversation just supplied the reasoning.

## Status lifecycle

```
proposed -> accepted -> implemented -> superseded
                     \-> deprecated       (or from any non-terminal state)
```

| Transition | Trigger |
|---|---|
| (none) → `proposed` | Drafted, approved, written — but real open questions remain |
| (none) → `accepted` | Drafted, approved, written — decision is already final |
| `proposed` → `accepted` | User confirms the open questions are resolved |
| `accepted` → `implemented` | User confirms the decision has actually shipped — this skill has no work-queue of its own, so this is always a direct confirmation, not automatic |
| any non-terminal → `superseded` | A new ADR replaces this one; link both directions (`supersedes` / `superseded-by`) and flip the old one's status |
| any non-terminal → `deprecated` | Retired with no successor |

`superseded` and `deprecated` are terminal — never transition out of them.
Never delete an ADR to "fix" it; supersede it instead. The chain is the
value.

## Operations

In Claude, invoke `/grumpy-senior-engineer-workflow:grumpy-adr <operation>
[target] [details]`. In Codex, select the plugin's `adr` skill or request an
operation naturally, for example "use Grumpy ADR to audit our decisions".

| Operation | Aliases | Effect |
|---|---|---|
| `new` | `create`, `record` | Runs the capture workflow above. |
| `show` | `get`, `read` | Runs the reading workflow above for `target` (an ADR number or keyword). |
| `list` | — | Prints `docs/adr/INDEX.md`, optionally filtered by status or tag from `details`. |
| `accept` | — | `proposed` → `accepted` for `target`, after confirming open questions are resolved. |
| `implement` | `ship` | `accepted` → `implemented` for `target`, after confirming it actually shipped. |
| `supersede` | — | Drafts a new ADR (via the capture workflow) that replaces `target`; on approval, writes it, sets `supersedes`/`superseded-by` on both records, and flips `target` to `superseded`. |
| `deprecate` | `retire` | Flips `target` to `deprecated`. `details` becomes the reason, recorded in Revision History. |
| `audit` | `lint`, `check` | Runs the checks below and reports pass/fail with file:issue citations. |
| `bootstrap` | `init` | Scaffolds `docs/adr/` in a repo that doesn't have it yet — see below. |

## Bootstrap

Triggered explicitly, or automatically the first time `new` targets a repo
without `docs/adr/`. Ask for confirmation before creating anything — same
consent gate as everything else in this skill. On confirmation, create:

- `docs/adr/` (directory)
- `docs/adr/INDEX.md` — headers only, no rows (copy the shape from
  `assets/templates/` or build it fresh: a table with columns ADR, Title,
  Type, Status, Date, Supersedes, Superseded by)
- `docs/adr/templates/capability-adr.md` and
  `docs/adr/templates/technology-adr.md` — copied verbatim from this
  skill's `assets/templates/`, so the repo has its own reference copy

Bootstrap never creates a numbered ADR. Numbers are for real, approved
decisions only — an empty template sitting at `0001` would make the
count in `INDEX.md` lie the moment anyone looks at it before the first
real decision lands.

Then check whether this documentation actually gets found later. A
`SKILL.md` only loads when something triggers it; the runtime loads applicable
`CLAUDE.md` or `AGENTS.md` instructions. Without a pointer there, an agent
that isn't already thinking about ADRs has no reason to go looking for
`docs/adr/` at all.

- If the repo has a root `CLAUDE.md` or `AGENTS.md` and it says nothing
  about `docs/adr/` or this skill, ask permission to add one short line
  — e.g. "Architecture decisions are recorded in `docs/adr/`; check
  `docs/adr/INDEX.md` before making or reversing one." One line, not a
  section; this is a pointer, not a copy of this skill's rules.
- If neither file exists, don't create one just to hold this pointer —
  that's a bigger call than this skill should make on its own. Say so
  plainly instead: without a pointer somewhere that loads automatically,
  `docs/adr/` will only get checked when this skill happens to trigger,
  not by default.

## Audit

Re-scan `docs/adr/` and check:

- Numbering is contiguous from `0001` — no gaps, no duplicates, no reuse
- Every file's `adr:` frontmatter value matches its own filename
- `INDEX.md` has exactly one row per file — nothing missing, nothing
  stale
- `status` is one of the five valid values
- `supersedes` / `superseded-by` are symmetric (if A supersedes B, B must
  point back and be marked `superseded`)
- Every ADR has a non-empty TL;DR, Consequences, and Agent guidance section
- The repo's root `CLAUDE.md` or `AGENTS.md` (if either exists) still
  references `docs/adr/` or this skill — flag it if the pointer from
  Bootstrap was declined, removed, or never added, so the gap doesn't
  sit unnoticed

Report each check as pass/fail; for failures, cite the specific file and
what's wrong (e.g. "ADR-0007: frontmatter says superseded-by ADR-0012,
but ADR-0012 has no supersedes field pointing back") — a vague "something's
off" isn't actionable, a specific citation is.

## What not to do

- Don't record trivial decisions — variable naming, formatting, anything
  that wouldn't cost someone real time to re-derive.
- Don't write essays. If Context needs more than five or six sentences,
  the decision is probably bigger than one ADR — consider splitting it.
- Don't write a numbered file before approval, ever.
- Don't hand-edit `INDEX.md` — regenerate it.
- Don't flip status without an explicit, confirmed operation.
- Don't dump a full ADR when answering "why did we choose X" — TL;DR +
  Decision + status is the right amount unless more is requested.

## Worked examples

**Recording a technology decision from natural conversation:**
> "we decided to use Postgres instead of Mongo for the billing service,
> mainly because we need transactions across the invoice and
> payment tables"

-> Recognizes the explicit decision signal, drafts a `technology` ADR
(Context: billing needs cross-table transactions; Decision: Postgres;
Rationale: names Mongo as the rejected alternative and why), presents it,
confirms it's final -> writes `docs/adr/0004-use-postgres-for-billing.md`
with `status: accepted`, regenerates `INDEX.md`.

**Reading a past decision:**
> "why does the billing service use Postgres instead of Mongo?"

-> Finds ADR-0004 in the index, answers with its TL;DR + Decision +
status, offers to show the full rationale if wanted.

**Superseding a decision:**
> "/grumpy-senior-engineer-workflow:grumpy-adr supersede 0004 we're moving
> billing to CockroachDB for multi-region writes"

-> Drafts the replacement ADR through the normal capture workflow, and
only on approval writes it, sets `0004`'s `superseded-by` and the new
ADR's `supersedes`, flips `0004` to `superseded`, regenerates `INDEX.md`.
