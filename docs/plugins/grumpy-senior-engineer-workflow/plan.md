# Planning

[Plugin overview](../../../plugins/grumpy-senior-engineer-workflow/README.md)

Every Plan-mode deliverable must contain ten sections, in order. Explain
why a section has no applicable changes instead of writing a bare "none":

| # | Section | # | Section |
| --- | --- | --- | --- |
| 1 | Non-negotiables | 6 | File tree |
| 2 | Decisions | 7 | Tests |
| 3 | Models | 8 | Size check |
| 4 | Functions | 9 | ADR check |
| 5 | Diagram | 10 | Documentation check |

Before any of that, the plan needs to be built on something real, not a
guessed-at goal — see "Before drafting" in the skill.

## Runtime hooks

In Claude Code, three `PreToolUse` hooks reinforce the workflow:

- On `EnterPlanMode`, a nudge reminds Claude to apply the checklist
  before it starts drafting, and a gate **denies** the tool call — sending
  Claude to ask the user via `AskUserQuestion` first — if the task itself
  lacks basic Context (what this touches, and why) or Scope (what "done"
  looks like). A missing design/approach preference is *not* grounds for
  denial; proposing one is the plan's job.
- On `ExitPlanMode`, a gate reads the drafted plan and **denies** the
  tool call — sending Claude back to fix the plan — if any section is
  missing or hollow, before presenting it for approval.

In Codex, `UserPromptSubmit` adds a conditional planning reminder. Before
presenting a plan, the skill runs a local structural preflight on the complete
envelope via stdin, correcting failures without saving an unapproved file.
A local `Stop` hook also checks plans whose final-message text consists entirely of one
`<proposed_plan>...</proposed_plan>` envelope. It requires the ten headings
exactly once, in order, with non-placeholder content. It accepts fenced
diagrams and file trees without treating their contents as headings.

In Codex 0.162.0, native Plan Mode supplies no final-message text to `Stop`,
so that path relies on the agent running the preflight. It is not an automatic
runtime guarantee; the agent must still await user approval.

The Codex Stop hook can request one correction. Neither check assesses plan
quality or establishes user approval. Ordinary replies and clarification
questions are left alone. See [Codex setup and limits](./codex.md).

Once approved, the plan is saved to `docs/plans/<slug>.md` so it
outlives the conversation that produced it. Saving may be skipped only
when implementation starts in the same turn and will finish before the
conversation could plausibly be interrupted. When in doubt, save first.

## Usage

Claude command example (Codex uses skill selection or natural language):

```text
/grumpy-senior-engineer-workflow:grumpy-plan add idempotent Kafka publishing to the billing service so retried messages don't double-charge a tenant
```

It also triggers from plain language — "how should we approach adding
dark mode?" or simply asking for something non-trivial enough that
the agent would plan on its own works without the slash command.

## How It Works

- **[`skills/plan/SKILL.md`](../../../plugins/grumpy-senior-engineer-workflow/skills/plan/SKILL.md)** is the single source of truth for the ten
  required plan sections and how to work with the user while drafting.
  [`skills/plan/references/ascii-diagrams.md`](../../../plugins/grumpy-senior-engineer-workflow/skills/plan/references/ascii-diagrams.md) holds sequence/class/state
  diagram templates for section 5.
- **[`commands/grumpy-plan.md`](../../../plugins/grumpy-senior-engineer-workflow/commands/grumpy-plan.md)** is a thin dispatcher for the explicit
  `/grumpy-senior-engineer-workflow:grumpy-plan` command, same pattern
  as the other two commands.
- **[`hooks/nudge-enter-plan.sh`](../../../plugins/grumpy-senior-engineer-workflow/hooks/nudge-enter-plan.sh)** runs on `PreToolUse` for
  `EnterPlanMode` and always allows — it only adds a reminder message
  so the checklist is in mind before drafting starts. It runs alongside
  (not instead of) the gate below — both are registered under the same
  `EnterPlanMode` matcher in [`hooks.json`](../../../plugins/grumpy-senior-engineer-workflow/hooks.json).
- The `EnterPlanMode` **gate** and the `ExitPlanMode` **gate** are both
  `prompt`-type hooks defined inline in [`hooks.json`](../../../plugins/grumpy-senior-engineer-workflow/hooks.json) (no script file).
  The entry gate reads the transcript for the user's request and denies
  the tool call if it lacks basic Context or Scope (see "Before
  drafting" in the skill). The exit gate reads the transcript for the
  drafted plan and denies the tool call if any of the ten sections is
  missing or hollow.
- [`hooks/codex-plan.py`](../../../plugins/grumpy-senior-engineer-workflow/hooks/codex-plan.py)
  handles Codex reminders and structural checks. `--check-plan` exits 0 for
  valid structure and 1 for a correction; hook events are registered in
  [`hooks.codex.json`](../../../plugins/grumpy-senior-engineer-workflow/hooks.codex.json).
