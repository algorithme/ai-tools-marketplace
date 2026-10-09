---
adr: NNNN
title: <specific, e.g. "Support multi-tenant billing">
type: capability
status: proposed
date: YYYY-MM-DD
deciders: [<name>, <name>]
supersedes: null
superseded-by: null
depends-on: []
tags: []
---

# ADR-NNNN: <Title>

## TL;DR

<One or two sentences. Someone skimming a hundred ADRs should know from
this line alone whether it matters to what they're doing.>

## Context

<2-5 sentences: what prompted this, what constraints applied. If this
needs more than ~6 sentences, the decision is probably bigger than one
ADR — consider splitting it.>

## Capability statement

<1-3 sentences: what the system will do that it didn't, or didn't
guarantee, before.>

## User stories / scenarios

- As a <role>, I want <capability>, so that <benefit>.

## Acceptance criteria

<Numbered and testable — "done" means these hold, not "code was written.">

1. <criterion>
2. <criterion>

## Out of scope

<What this explicitly does NOT cover, so scope doesn't quietly creep in
later under the same ADR number.>

## Open questions

<Anything still unresolved. Delete this section (or resolve everything in
it) before moving status past `proposed` — an ADR can't be `accepted`
while this still has open items.>

## Consequences

**Positive:** <what this unlocks, and for whom>
**Negative:** <what this costs — new maintenance burden, complexity, things
that get harder once this ships>
**Risks:** <what could go wrong, and under what condition this should be revisited>

## Agent guidance

<One or two sentences addressed directly to an AI agent working in this
codebase: what should it do differently because this ADR exists? E.g.
"Any new tenant-scoped feature must pass the tenant_id boundary described
here; if a task seems to require breaking that boundary, stop and surface
the conflict with this ADR before implementing.">

## References

<Links: PRs, docs, related ADRs, design mocks.>

## Revision History

| Date | Change | By |
|---|---|---|
| YYYY-MM-DD | Created | <name> |
