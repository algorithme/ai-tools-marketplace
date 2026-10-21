---
name: ponytail-help
description: >-
  Explain this marketplace's Ponytail commands, modes, setup, and limitations.
  Use for ponytail-help or questions about using Ponytail. Display help without
  changing modes, installing anything, or writing configuration.
license: MIT
---

# Ponytail help — olivier-vault edition

Answer the user's question using this reference. Help is a one-shot display
that does not enable the persona or write any files. Do not imply a setting
changed just because this skill was loaded.

## Commands

Use a standalone message for mode commands. Claude Code's packaged entrypoint
is `/ponytail:ponytail`; Codex uses `$ponytail:ponytail`. The hook also accepts
the short `/ponytail` and `$ponytail` forms when delivered as user text.

| Suffix | Result |
|---|---|
| none | Report the active mode; if off, enable the default, or full when the default is off. |
| lite | Build the requested solution and offer a smaller alternative. |
| full | Prefer the smallest complete implementation. Initial default. |
| ultra | Question unnecessary work while respecting settled choices. |
| off | Retire the persona in this conversation. |
| default lite/full/ultra/off | Set one chosen mode for future conversations in this host. |

For example, `/ponytail:ponytail default lite` or
`$ponytail:ponytail ultra`. “Stop ponytail” and “normal mode” also turn it off
when sent alone. Commands inside prose or code fences do not change settings.
Only the hook's confirmation establishes a persisted change.

## Reports

Invoke `/ponytail:ponytail-review`, `/ponytail:ponytail-audit`,
`/ponytail:ponytail-debt`, or `/ponytail:ponytail-help` in Claude Code.
In Codex replace the initial slash with `$`. Review checks a change; audit
checks a repository scope; debt lists intentional shortcuts. These remain
available while off and do not change the stored mode or edit code.

## Setup and persistence

This custom package requires Node.js 24+ on macOS or Linux and compatible local
Claude Code/Codex plugin hooks. Review and trust hooks through the host's normal
flow. Installation does not establish trust. See the [plugin README](../../README.md).

Modes are private to each conversation and survive resume and compaction.
New, cleared, or forked conversations use that host's saved default. Defaults
and mode-only records live under the host's plugin data directory in
`ponytail-v1/<host>/`. No transcripts, project content, or prompts are stored.
There is no fallback to upstream's configuration or environment defaults.

Without usable hooks, explicitly requested skills still give task-local
guidance; they cannot persist a mode. This edition has no board, telemetry,
webhook, source mapper, status-line integration, or benchmark scoreboard.
Use one Ponytail edition at a time to avoid duplicate guidance. Update through
the `olivier-vault` marketplace's normal host flow, then review changed hooks.

Adapted by Olivier Morel from [Ponytail by Dietrich Gebert (DietrichGebert)](https://github.com/DietrichGebert/ponytail/tree/09c434ab73ca43761c5d8b0c5d341926c2fba710), under the [MIT license](../../LICENSE).
