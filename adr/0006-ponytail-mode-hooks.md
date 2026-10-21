# 0006 — Focused Ponytail adapter with conversation-isolated state

**Status**: Accepted

## Context

Ponytail by Dietrich Gebert (DietrichGebert) combines coding guidance with a
broader runtime. This marketplace needs five shared skills and conversation
modes for Claude Code and Codex, with explicit attribution and a bounded review
surface. The approved custom edition starts from upstream 5.3.2 at
`09c434ab73ca43761c5d8b0c5d341926c2fba710`.

## Decision

Keep one `plugins/ponytail` package, matching 1.0.0 Claude/Codex manifests, shared
skills, and separate hook registrations, following ADRs 0001, 0002, and 0005.
Maintain a focused CommonJS adapter using Node.js 24 or a newer supported release
and built-in modules only. Support macOS and Linux; CI validates on Node 24.

Use host-provided plugin data only, with separate host directories, hashed
session filenames, private files, and atomic writes. Startup, clear, and fork
use a separately stored default, initially full. Resume and compaction restore
the conversation's mode; subagents inherit it without changing it. Only exact
user commands change modes or future defaults. Missing storage disables
persistence without project or user-settings fallbacks.

Retain coding, review, audit, debt, and help. Exclude board, metrics, webhooks,
transcript imports, source mapping, status-line setup, scoreboard, and other
assistant integrations. Preserve the original MIT notice and author credit;
Olivier Morel maintains this independently versioned adaptation.

Importing the full upstream runtime was rejected because its integrations and
shared configuration exceed the requested scope. Reusing Grumpy's Python runtime
would avoid a separate language for hooks, but the approved scope keeps this
adapter aligned with upstream's Node runtime. Instruction-only skills cannot
reliably preserve per-conversation mode across host lifecycle events.

## Consequences

### Positive

- Shared skills remain discoverable, with a small runtime and no npm dependencies.
- Conversation state is independent of working directory and other sessions.
- Explicit safety evidence covers the shipped package rather than certifying upstream.

### Negative / trade-offs

- Node and supported host hook contracts become runtime prerequisites.
- The adapter and two launchers need independent maintenance and fresh review of imports.
- Saved mode files accumulate for resume; guidance is not an enforcement boundary.

### Neutral

- Normal host hook trust review remains required; no trust settings are installed.
- Following ADR 0003, `scripts/validate.sh` blocks on executable hook tests.
- Native installation/trust smoke checks remain separate from offline validation.

## Agent guidance

Keep mode/default writes inside the adapter and host data area. Preserve settled
user choices and Grumpy workflows. Review future upstream imports against this
scope, renew the [safety assessment](../docs/plugins/ponytail/security-review.md),
and retain [upstream attribution](../plugins/ponytail/README.md).
