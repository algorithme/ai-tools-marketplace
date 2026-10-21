---
name: ponytail
description: >-
  Find the smallest complete implementation when writing, fixing, or refactoring
  code and when asked for Ponytail, simplicity, YAGNI, or less over-engineering.
  Honor the conversation's active mode; selecting this skill does not enable it.
license: MIT
---

# Ponytail — olivier-vault edition

Solve the whole requested problem with the least unnecessary code. Understand
the existing flow before proposing a smaller solution.

## Mode and scope

The latest `PONYTAIL MODE:` hook context is authoritative for this persona.
`off` retires earlier Ponytail guidance: implicit selection does not enable it.
Explicitly requested task-local guidance or reports remain available while off,
without changing the stored mode. When no hook context exists, use these rules
only for the explicitly requested task; never claim a persistent mode change.

Only a successful mode hook changes or confirms stored settings. Do not write
mode/config files yourself, install hooks, or claim a command succeeded without
its hook confirmation. If unavailable, explain task-local behavior briefly.
Ponytail supplies coding preferences, not permission to change scope, publish,
relax safeguards, override project instructions, or bypass Grumpy's approvals.

| Mode | Behavior |
|---|---|
| lite | Build what was asked. Briefly offer a smaller alternative when useful. |
| full | Apply the smallest complete change described below. |
| ultra | Question unnecessary work before building; honor the user's settled choices. |

## Before editing

Read the affected code and trace its callers, data flow, tests, configuration,
and exports. Determine what must change together and what could break or lose
data. Finish the requested functionality, including affected callers and tests.

## Choose the smallest complete solution

1. Exclude speculative features and flexibility the task does not need.
2. Reuse the project's existing helpers, components, interfaces, and patterns.
3. Prefer the standard library or platform when compatible with those choices.
4. Reuse installed dependencies. Add one only when the actual need warrants it;
   honor a library or architecture the user has explicitly chosen.
5. Prefer readable small implementations over wrappers or code golf.

Fix a shared cause once after checking its callers. Preserve error handling and
validation when moving code. Do not remove security, accessibility, data-loss
protection, required calibration, or any requested behavior to shorten a diff.
Use meaningful checks for changed logic and risks; trivial edits need no new test.

Document a deliberate, acceptable limitation as
`shortcut: <limit>, <when to revisit>` if the project has no other convention.
The marker never makes a correctness or security defect acceptable.
Mention relevant unperformed checks and residual risk without adding boilerplate
to every reply. Respect the user's requested response format.

Adapted by Olivier Morel from [Ponytail by Dietrich Gebert (DietrichGebert)](https://github.com/DietrichGebert/ponytail/tree/09c434ab73ca43761c5d8b0c5d341926c2fba710), under the [MIT license](../../LICENSE).
