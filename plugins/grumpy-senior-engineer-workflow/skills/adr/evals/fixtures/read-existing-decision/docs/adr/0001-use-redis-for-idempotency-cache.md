---
adr: 1
title: Use Redis for idempotency cache
type: technology
status: accepted
date: 2026-10-01
deciders: [checkout service team]
supersedes: null
superseded-by: null
depends-on: []
tags: [checkout, idempotency, redis]
---

# ADR-0001: Use Redis for idempotency cache

## TL;DR

Use Redis for the checkout idempotency-key cache instead of a custom
Postgres dedupe table. Redis provides built-in TTL expiration, and the
payments team's existing Redis cluster can be reused.

## Context

The checkout service needs to remember idempotency keys during a bounded
retry window. Expired keys must be removed without adding a custom cleanup
job. The payments team already operates a Redis cluster available to the
checkout service.

## Decision

Store checkout idempotency keys in the existing payments Redis cluster and
use Redis TTLs to expire them after the retry window.

## Rationale

Redis provides the expiration mechanism we need and avoids operating a new
cluster by reusing the payments team's deployment.

- **Custom Postgres dedupe table** — Rejected because it would require
  custom expiration and cleanup logic that Redis already provides.

## Consequences

**Positive:** Built-in TTL support reduces custom cleanup code, and reusing
the existing cluster avoids provisioning a separate service.

**Negative:** Checkout becomes dependent on the shared Redis cluster and
must coordinate capacity and availability requirements with payments.

**Risks:** An unsuitable TTL or eviction policy could remove keys before
the retry window ends. Confirm both before deploying the cache.

## Agent guidance

Use the shared Redis cluster and TTL expiration for checkout idempotency
keys. Surface any proposal to replace this with a Postgres dedupe table
as a conflict with this ADR before changing the design.

## References

The checkout decision captured by the `technology-decision-with-bootstrap`
evaluation scenario.

## Revision History

| Date | Change | By |
|---|---|---|
| 2026-10-01 | Accepted the Redis decision | checkout service team |
