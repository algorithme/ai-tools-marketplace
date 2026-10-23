# 0007 — Grumpy coordinates optional Ponytail workflows

**Status**: Accepted

## Context

Grumpy owns planning and approved implementation. Ponytail supplies coding
guidance and read-only audit, review, and debt reports. Using them independently
leaves those reports disconnected from planning and verification. This decision
extends [ADR 0005](./0005-dual-runtime-grumpy.md) and
[ADR 0006](./0006-ponytail-mode-hooks.md).

## Decision

Grumpy retains ownership of scope, approval, implementation, and completion
review. Discover optional Ponytail capabilities through the host's available
skills. Substantial work gets a scoped audit and an independent design challenge;
implementation reviews planned contract boundaries and the cumulative task
change, and compares documented shortcuts before and after the work.

Keep persona mode separate: Grumpy never changes stored Ponytail modes or
defaults, and reports remain usable while the persona is off. Missing companion
skills or reviewers fall back to applicable Grumpy and repository checks, with
honest disclosure of same-agent review and reduced independence.

Preserve existing commands, the ten plan sections, runtime hooks, and explicit
user approval. Keep evidence in the approved plan and completion report, without
a new workflow database, mandatory ledger, or telemetry.

Reject a required Ponytail dependency because it breaks standalone Grumpy.
Reject shared hook or mode state because it duplicates Ponytail's ownership.

## Consequences

### Positive

- Earlier findings shape design and targeted tests.
- Review remains available when Ponytail is unavailable or its persona is off.

### Negative / trade-offs

- Independent reviews cost time and model usage; stages must remain proportionate.
- Guidance depends on compliance; structural checks prove neither quality nor approval.

### Neutral

- The paired workflow pilot supplies observational evidence, not a quality guarantee.

## Agent guidance

State the scope and starting baseline explicitly. Reviewers report findings;
the implementer validates them, makes corrections, and verifies the result.
Preserve settled user choices and unrelated user work. Use the
[pilot report](../docs/plugins/grumpy-senior-engineer-workflow/ponytail-evaluation.md)
for this release's scope and evidence.
