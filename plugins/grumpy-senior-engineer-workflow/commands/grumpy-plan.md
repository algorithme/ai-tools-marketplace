---
description: Plan a new task using the required checklist structure, then enter Plan Mode
argument-hint: <task description>
---

Apply the rules in the `plan` skill (`grumpy-senior-engineer-workflow:plan`)
to the task below. If that skill isn't loaded yet, load it first — it is
the single source of truth for the ten required plan sections, how to
work with the user while drafting (context before the question, plain
language, small over clever), and which companion skills to consult.
Do not reimplement those rules here; this command only hands off to
them.

Task: $ARGUMENTS

Enter Plan Mode for this task (via `EnterPlanMode`) if it isn't already
active, draft the plan following all ten sections from the `plan`
skill in order, and only then call `ExitPlanMode`. An `ExitPlanMode`
hook checks the same ten sections before the user sees the plan — treat
that as a backstop, not the target; get it right on the first draft.
