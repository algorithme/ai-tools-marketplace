---
name: context
description: >-
  Manages a minimal, machine-readable project context stored under
  .contexts/ (index.md for the root project plus one file per monorepo
  subproject, each capped at 500 characters and deduplicated against
  every CLAUDE.md in the repo). Use this PROACTIVELY whenever the user
  wants to view, record, refresh, or reset what an AI agent should know
  about a project or a subproject — even if they don't say "context"
  explicitly. Triggers include: "what's the context for the api
  service?", "update the project context, we moved to Postgres",
  "reset the context", "add a context for the frontend subproject",
  "remember that this service does X", or starting work in an
  unfamiliar subproject of a monorepo and needing a quick orientation.
  Also triggers on the explicit slash command
  /grumpy-senior-engineer-workflow:grumpy-context.
---

# Context

A grumpy senior engineer does not write a memoir for every service —
they leave a terse note on the whiteboard: what it is, what's
non-obvious, nothing you could read in the README. That's what
`.contexts/` holds: a cheat-sheet for AI agents, not a second
`CLAUDE.md`. If you're about to write a paragraph, you're doing it
wrong — cut it down.

## Storage layout

```
project_root/.contexts/
  index.md            # root project context + manifest of subprojects
  <subproject>.md      # one file per monorepo subproject
```

`<subproject>` is a kebab-case name (derived from the subproject's
directory name unless the user says otherwise). Never name one
`index` — that slot is reserved for the root. A name identifies at
most one directory: if the user's chosen name is already registered
for a *different* path, that's a collision — ask them to disambiguate
(e.g. `billing-api` vs `billing-worker`) rather than silently
overwriting or merging two unrelated subprojects.

`index.md` holds both the root context and the manifest in one file:

```markdown
# Project Context

## Context
<root context body — see "Writing a context body" below>

## Subprojects
| Context file | Path | Scope |
|---|---|---|
| api-service.md | apps/api-service | one-line description of the subproject |
| frontend.md | apps/frontend | one-line description of the subproject |
```

The `Path` column is what makes a subproject unambiguous — it's the
directory the context describes, relative to the project root.

A subproject file (`.contexts/<name>.md`) records its own path too:

```markdown
# <name>
Path: <path relative to project root>

<context body — see "Writing a context body" below>
```

The `## Subprojects` table only exists in `index.md`. If there are no
subprojects yet, omit the section entirely rather than leaving it empty.

## Writing a context body

The **body** is the part that answers "what would an agent need to
know that it can't get elsewhere." Everything else in this skill
exists to protect that one paragraph. Rules for it:

1. **≤ 500 characters, no exceptions.** Verify by piping the draft
   through `wc -m` (or equivalent) — don't eyeball it. If it doesn't
   fit, cut adjectives and examples before cutting facts.
2. **Deduplicated against every `CLAUDE.md` in scope.** Before writing
   or merging, find and read them:
   ```bash
   find . -name CLAUDE.md -not -path '*/.git/*' -not -path '*/node_modules/*' \
     -not -path '*/.venv/*' -not -path '*/dist/*' -not -path '*/build/*' \
     -not -path '*/target/*' -not -path '*/vendor/*' -not -path '*/__pycache__/*'
   ```
   Read the root `CLAUDE.md` plus any nested one under the target's
   own directory tree (use the subproject's `Path` from the manifest —
   a subproject only needs its own nested file(s), not siblings').
   Anything already stated there — stack, structure,
   commands, conventions — does not belong in the context. Store only
   the delta: things CLAUDE.md doesn't say and an agent would otherwise
   have to rediscover (e.g. "the retry logic in `billing/` is
   intentionally duplicated, don't unify it", "auth service is legacy,
   being replaced by `svc-auth-v2`, don't add features to it").
3. **Markdown, minimal, for machines.** No headers inside the body, no
   marketing language ("robust", "powerful", "seamless"), no restating
   the obvious. Plain factual sentences, semicolon- or period-separated.
4. **One paragraph, not a list of everything you know.** If a fact
   doesn't change how an agent should act, it doesn't earn a slot.

## Operations

Invoked via `/grumpy-senior-engineer-workflow:grumpy-context <operation>
[target] [details]`, or triggered directly from natural language.
`target` defaults to the root (`index.md`'s `## Context`) when omitted.

| Operation | Aliases | Effect |
|---|---|---|
| `get` | `show`, `retrieve` | Read and return the current context. No target -> root context plus the subproject table. Named target -> that subproject's body only. |
| `set` | `reset` | Replace the target's body wholesale with a fresh one derived from `details`. Used when the old context is stale or wrong, not just incomplete. |
| `improve` | `update`, `add` | Merge `details` into the existing body. Never silently drop prior facts — if the merge would exceed 500 characters, rewrite the *whole* body tighter so everything still fits (compress-to-fit), rather than truncating or refusing. |
| `add-sub` | `add-sub-context`, `add-subcontext` | Create `.contexts/<name>.md` for a new subproject, recording its `Path`, and add a matching row to `index.md`'s `## Subprojects` table. If the name already exists for the same path, stop and suggest `improve` instead — don't overwrite silently. If the name exists for a *different* path, that's a collision — ask the user to disambiguate. |

Shared behavior across all operations:

- If `.contexts/` or `index.md` doesn't exist yet, `set`/`improve`/
  `add-sub` create them on demand. `get` does not — if nothing is
  stored, say so plainly ("no context recorded yet for this project")
  instead of inventing one.
- If `index.md` exists but doesn't match the expected format (missing
  `## Context` section, a `## Subprojects` table with broken rows,
  etc.), don't guess at a repair. Show the user what's malformed and
  ask how to proceed before overwriting anything — a bad merge into a
  broken file is harder to undo than a short pause.
- After any write, re-read the file and confirm it parses and the
  body is within the limit. A context that fails its own rules is
  worse than no context.
- Confirm the CLAUDE.md dedup check happened before writing — mention
  briefly what was excluded because it was already covered there, so
  the user can catch a bad merge.

## Worked examples

**Set the root context in a fresh repo:**
```
/grumpy-senior-engineer-workflow:grumpy-context set root this is a monorepo with an api-service (FastAPI) and a frontend (React); shared Postgres instance; deploys via the shared Terraform in infra/
```
-> creates `.contexts/index.md` with a body under 500 chars, skipping
anything the root `CLAUDE.md` already documents (e.g. if CLAUDE.md
already says "FastAPI + React monorepo", that part is dropped).

**Add a subproject:**
```
/grumpy-senior-engineer-workflow:grumpy-context add-sub api-service at apps/api-service; handles billing and auth; auth is legacy and being replaced by svc-auth-v2, don't extend it
```
-> creates `.contexts/api-service.md` with `Path: apps/api-service`
and adds a matching row to the `## Subprojects` table in `index.md`.
If the path isn't stated explicitly, infer it from the directory named
`api-service` and confirm it with the user.

**Improve an existing subproject context:**
```
/grumpy-senior-engineer-workflow:grumpy-context improve api-service we just migrated the billing retry logic to use idempotency keys
```
-> reads the existing body, merges the new fact in, compresses if
needed to stay ≤ 500 chars.

**Retrieve context (often triggered without the slash command):**
> "what's the context for the frontend subproject?"
-> `get frontend`: read and return `.contexts/frontend.md`'s body
verbatim (or report that none exists yet).

**Reset because the old context is wrong:**
```
/grumpy-senior-engineer-workflow:grumpy-context reset frontend scrap the old notes, this got rewritten from Vue to React this quarter
```
-> replaces the whole body rather than merging (the old facts are no
longer true, so `improve` would be wrong here).