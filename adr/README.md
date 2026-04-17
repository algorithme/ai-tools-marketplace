# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the `ai-tools-marketplace` project. An ADR captures a significant architectural choice, the context that motivated it, and the trade-offs accepted.

## Index

| # | Title | Status |
|---|-------|--------|
| [0001](./0001-monorepo-with-relative-paths.md) | Monorepo layout with relative-path plugin sources | Accepted |
| [0002](./0002-versioning-and-releases.md) | Versioning strategy — semver in `plugin.json` | Accepted |
| [0003](./0003-validation-and-ci.md) | Validation authority — `scripts/validate.sh` + best-effort CI | Accepted |
| [0004](./0004-documentation-structure.md) | Documentation structure — modular files over monolithic guides | Accepted |

## When to write an ADR

Write an ADR for any decision that is:
- Hard to reverse (directory layout, naming conventions, schema shape).
- Non-obvious to a future contributor reading the repo cold.
- A trade-off between two reasonable approaches.

You do **not** need an ADR for style preferences, obvious choices, or decisions fully captured in a PR description.

## Template

Copy this into a new file named `NNNN-short-title.md`:

```markdown
# NNNN — Title

**Status**: Proposed | Accepted | Deprecated | Superseded by [XXXX](./XXXX-title.md)

## Context

What is the problem or situation that motivated this decision?

## Decision

What did we decide to do?

## Consequences

### Positive
- …

### Negative / trade-offs
- …

### Neutral
- …
```
