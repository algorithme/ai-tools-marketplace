# 0005 — Shared Grumpy package with separate runtime hooks

**Status**: Accepted

## Context

Grumpy's Claude prompt hooks and EnterPlanMode/ExitPlanMode matchers do not work
in Codex. Skills and startup readers can be shared, but claiming identical hook
enforcement would mislead users. The approved 1.4.0 plan adds Codex support without
forking the plugin or changing its stored context, ADR or plan formats.

## Decision

Keep one marketplace entry and plugin directory. Preserve the Claude manifest,
commands and prompt hooks. Add a Codex compatibility manifest selecting its own
command-only hooks and the same four skills. Keep both manifest versions equal;
this extends [ADR 0002](./0002-versioning-and-releases.md).

Codex receives startup readers, a planning reminder and a stateless Python 3
structural check for complete plan envelopes. Its planning skill runs that check
explicitly through stdin before presenting a plan. Stop also checks final text
when available and can request one correction. Native testing on Codex 0.162.0
showed Plan Mode emits a structured plan and passes null final text to Stop;
the user approved the preflight command to cover that gap without transcript
parsing or saved state. Preflight depends on the agent invoking it.

Neither check evaluates quality, hides already-visible output or grants user
approval. Use the runtime's hook review flow, without installing trust decisions.

Reject separate plugin forks because they duplicate skills and release work.
Reject model-backed hook emulation because it adds credentials, cost and network
dependencies. Keep Claude's semantic prompt checks where that runtime supports them.

Extend [ADR 0003](./0003-validation-and-ci.md)'s validator with runtime-specific
manifest validation, identity/path checks and executable hook tests. Native Codex
smoke tests remain separate from the offline validator.

## Consequences

### Positive
- Shared workflows and formats stay consistent across runtimes.
- Codex hooks run locally without external services or stored hook state.

### Negative / trade-offs
- Codex requires Python 3 and Bash; two manifest versions must remain synchronized.
- Structural checks cannot prove completeness or approval; Stop alone cannot check native Plan Mode plans.

### Neutral
- Users review new or changed hooks; installation alone does not activate them.
- Runtime support must be described per plugin, not inferred for the whole marketplace.
