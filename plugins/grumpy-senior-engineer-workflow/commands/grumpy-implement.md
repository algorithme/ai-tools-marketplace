---
description: Implement an approved plan, following the same guardrails it was built under
argument-hint: <path to plan file, e.g. docs/plans/foo.md> (omit to use the plan just approved this session)
---

Apply the rules in the `implement` skill
(`grumpy-senior-engineer-workflow:implement`) to the plan below. If that
skill isn't loaded yet, load it first — it is the single source of
truth for how to locate the plan, how each of the ten plan sections
becomes actionable during a build, when a deviation needs the user's
input versus when it can just proceed, and which companion skills
(`adr`, `fastapi-resilience`, `context`) to consult along the way. Do
not reimplement those rules here; this command only resolves the plan
argument and hands off to them.

Plan argument: $ARGUMENTS

Resolve it as follows:

- **A path was given** — read that file as the plan to implement.
- **No argument was given** — if a plan was drafted and approved via
  `ExitPlanMode` earlier in this conversation, use that plan directly.
  Otherwise, ask the user which plan to implement rather than guessing.

Then carry out the build exactly as the `implement` skill specifies,
including confirming the plan still has all ten sections before
starting, saving an unsaved plan to `docs/plans/` unless the `plan`
skill's narrow same-turn exception applies, enforcing non-negotiables
rather than just noting them, and pausing to ask before any real
deviation from the plan's Decisions, Models, Functions, or File tree.
