---
adr: NNNN
title: <specific, e.g. "Use Postgres instead of MongoDB for primary storage">
type: technology
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

## Decision

<1-3 sentences, stated plainly: what was decided.>

## Rationale

<Why this option, specifically. Name every alternative seriously
considered and why it was rejected — "we didn't have time to evaluate X"
is a valid reason, but say so; don't omit an alternative just because the
answer looks obvious in hindsight.>

- **<Alternative A>** — Why not: <reason>
- **<Alternative B>** — Why not: <reason>

## Consequences

**Positive:** <what this buys us>
**Negative:** <what this costs us>
**Risks:** <what could go wrong, and under what condition this should be revisited>

## Agent guidance

<One or two sentences addressed directly to an AI agent working in this
codebase: what should it do differently because this ADR exists? E.g.
"Default to Postgres for any new persistent storage in this service; if a
task seems to need a different store, stop and surface the conflict with
this ADR before implementing rather than deciding unilaterally.">

## References

<Links: PRs, docs, related ADRs, benchmarks.>

## Revision History

| Date | Change | By |
|---|---|---|
| YYYY-MM-DD | Created | <name> |
